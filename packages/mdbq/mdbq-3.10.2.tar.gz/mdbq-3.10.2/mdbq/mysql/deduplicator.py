# -*- coding:utf-8 -*-
import datetime
import re
import time
from functools import wraps
import warnings
import pymysql
import os
from mdbq.log import mylogger
from typing import List, Dict, Optional, Any, Tuple, Set
from dbutils.pooled_db import PooledDB
import threading
import concurrent.futures
from collections import defaultdict


warnings.filterwarnings('ignore')
logger = mylogger.MyLogger(
    name='deduplicator',
    logging_mode='both',
    log_level='info',
    log_file='deduplicator.log',
    log_format='json',
    max_log_size=50,
    backup_count=5,
    enable_async=False,  # 是否启用异步日志
    sample_rate=1,  # 采样50%的DEBUG/INFO日志
    sensitive_fields=[],  #  敏感字段列表
)


class MySQLDeduplicator:
    """
    MySQL数据去重

    功能：
    1. 自动检测并删除MySQL数据库中的重复数据
    2. 支持全库扫描或指定表处理
    3. 支持多线程/多进程安全处理
    4. 完善的错误处理和日志记录

    使用示例：
    deduplicator = MySQLDeduplicator(
        username='root',
        password='password',
        host='localhost',
        port=3306
    )

    # 全库去重
    deduplicator.deduplicate_all()

    # 指定数据库去重(多线程)
    deduplicator.deduplicate_database('my_db', parallel=True)

    # 指定表去重(使用特定列)
    deduplicator.deduplicate_table('my_db', 'my_table', columns=['name', 'date'])

    # 关闭连接
    deduplicator.close()
    """

    def __init__(
            self,
            username: str,
            password: str,
            host: str = 'localhost',
            port: int = 3306,
            charset: str = 'utf8mb4',
            max_workers: int = 1,
            batch_size: int = 1000,
            skip_system_dbs: bool = True,
            max_retries: int = 3,
            retry_interval: int = 5,
            pool_size: int = 5
    ):
        """
        初始化去重处理器

        :param username: 数据库用户名
        :param password: 数据库密码
        :param host: 数据库主机，默认为localhost
        :param port: 数据库端口，默认为3306
        :param charset: 字符集，默认为utf8mb4
        :param max_workers: 最大工作线程数，默认为1(单线程)
        :param batch_size: 批量处理大小，默认为1000
        :param skip_system_dbs: 是否跳过系统数据库，默认为True
        :param max_retries: 最大重试次数
        :param retry_interval: 重试间隔(秒)
        :param pool_size: 连接池大小
        """
        # 连接池状态标志
        self._closed = False

        # 初始化连接池
        self.pool = PooledDB(
            creator=pymysql,
            host=host,
            port=port,
            user=username,
            password=password,
            charset=charset,
            maxconnections=pool_size,
            cursorclass=pymysql.cursors.DictCursor
        )

        # 配置参数
        self.max_workers = max(1, min(max_workers, 20))  # 限制最大线程数
        self.batch_size = batch_size
        self.skip_system_dbs = skip_system_dbs
        self.max_retries = max_retries
        self.retry_interval = retry_interval

        # 线程安全控制
        self._lock = threading.Lock()
        self._processing_tables = set()  # 正在处理的表集合

        # 系统数据库列表
        self.SYSTEM_DATABASES = {'information_schema', 'mysql', 'performance_schema', 'sys'}

    def _get_connection(self):
        """从连接池获取连接"""
        if self._closed:
            raise ConnectionError("连接池已关闭")
        try:
            conn = self.pool.connection()
            logger.debug("成功获取数据库连接")
            return conn
        except Exception as e:
            logger.error(f"获取数据库连接失败: {str(e)}")
            raise ConnectionError(f"连接数据库失败: {str(e)}")

    @staticmethod
    def _retry_on_failure(func):
        """重试装饰器"""

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            for attempt in range(self.max_retries + 1):
                try:
                    return func(self, *args, **kwargs)
                except (pymysql.OperationalError, pymysql.InterfaceError) as e:
                    last_exception = e
                    if attempt < self.max_retries:
                        wait_time = self.retry_interval * (attempt + 1)
                        logger.warning(
                            f"数据库操作失败，准备重试 (尝试 {attempt + 1}/{self.max_retries})",
                            {'error': str(e), 'wait_time': wait_time})
                        time.sleep(wait_time)
                        continue
                except Exception as e:
                    last_exception = e
                    logger.error(f"操作失败: {str(e)}", {'error_type': type(e).__name__})
                    break

            if last_exception:
                raise last_exception
            raise Exception("未知错误")

        return wrapper

    @_retry_on_failure
    def _get_databases(self) -> List[str]:
        """获取所有非系统数据库列表"""
        sql = "SHOW DATABASES"

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                all_dbs = [row['Database'] for row in cursor.fetchall()]

                if self.skip_system_dbs:
                    return [db for db in all_dbs if db.lower() not in self.SYSTEM_DATABASES]
                return all_dbs

    @_retry_on_failure
    def _get_tables(self, database: str) -> List[str]:
        """获取指定数据库的所有表"""
        sql = "SHOW TABLES"

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"USE `{database}`")
                cursor.execute(sql)
                return [row[f'Tables_in_{database}'] for row in cursor.fetchall()]

    @_retry_on_failure
    def _get_table_columns(self, database: str, table: str) -> List[str]:
        """获取表的列名(排除id列)"""
        sql = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (database, table))
                return [row['COLUMN_NAME'] for row in cursor.fetchall()
                        if row['COLUMN_NAME'].lower() != 'id']

    def _acquire_table_lock(self, database: str, table: str) -> bool:
        """获取表处理锁，防止并发处理同一张表"""
        key = f"{database}.{table}"

        with self._lock:
            if key in self._processing_tables:
                logger.debug(f"表 {key} 正在被其他线程处理，跳过")
                return False
            self._processing_tables.add(key)
            return True

    def _release_table_lock(self, database: str, table: str):
        """释放表处理锁"""
        key = f"{database}.{table}"

        with self._lock:
            if key in self._processing_tables:
                self._processing_tables.remove(key)

    def _deduplicate_table(
            self,
            database: str,
            table: str,
            columns: Optional[List[str]] = None,
            dry_run: bool = False
    ) -> Tuple[int, int]:
        """
        执行单表去重

        :param database: 数据库名
        :param table: 表名
        :param columns: 用于去重的列(为None时使用所有列)
        :param dry_run: 是否模拟运行(只统计不实际删除)
        :return: (重复行数, 删除行数)
        """
        if not self._acquire_table_lock(database, table):
            return (0, 0)

        try:
            logger.info(f"开始处理表: {database}.{table}")

            # 获取实际列名
            all_columns = self._get_table_columns(database, table)
            if not all_columns:
                logger.warning(f"表 {database}.{table} 没有有效列(可能只有id列)，跳过")
                return (0, 0)

            # 使用指定列或所有列
            use_columns = columns or all_columns
            invalid_columns = set(use_columns) - set(all_columns)

            if invalid_columns:
                logger.warning(
                    f"表 {database}.{table} 中不存在以下列: {invalid_columns}，使用有效列",
                    {'invalid_columns': invalid_columns}
                )
                use_columns = [col for col in use_columns if col in all_columns]

            if not use_columns:
                logger.error(f"表 {database}.{table} 没有有效的去重列")
                return (0, 0)

            # 构建去重SQL
            column_list = ', '.join([f'`{col}`' for col in use_columns])
            # temp_table = f"temp_{table}_{int(time.time())}"
            temp_table = f"temp_{table}_dedup_{os.getpid()}"  # 使用进程ID构建临时表
            temp_table = re.sub(r'[^a-zA-Z0-9_]', '_', temp_table)  # 确保表名合法

            # 使用临时表方案处理去重，避免锁表问题
            create_temp_sql = f"""
            CREATE TABLE `{database}`.`{temp_table}` AS
            SELECT MIN(`id`) as `min_id`, {column_list}, COUNT(*) as `dup_count`
            FROM `{database}`.`{table}`
            GROUP BY {column_list}
            HAVING COUNT(*) > 1
            """

            delete_dup_sql = f"""
            DELETE FROM `{database}`.`{table}`
            WHERE `id` NOT IN (
                SELECT `min_id` FROM `{database}`.`{temp_table}`
            ) AND ({' OR '.join([f'`{col}` IS NOT NULL' for col in use_columns])})
            """

            drop_temp_sql = f"DROP TABLE IF EXISTS `{database}`.`{temp_table}`"

            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # 创建临时表统计重复数据
                    cursor.execute(create_temp_sql)
                    cursor.execute(f"SELECT COUNT(*) as cnt FROM `{database}`.`{temp_table}`")
                    dup_count = cursor.fetchone()['cnt']

                    if dup_count == 0:
                        logger.info(f"表 {database}.{table} 没有重复数据")
                        cursor.execute(drop_temp_sql)
                        conn.commit()
                        return (0, 0)

                    logger.info(
                        f"表 {database}.{table} 发现 {dup_count} 组重复数据",
                        {'columns': use_columns}
                    )

                    if not dry_run:
                        # 执行实际删除
                        cursor.execute(delete_dup_sql)
                        affected_rows = cursor.rowcount
                        conn.commit()
                        logger.info(
                            f"表 {database}.{table} 已删除 {affected_rows} 行重复数据",
                            {'columns': use_columns}
                        )
                    else:
                        affected_rows = 0
                        logger.info(
                            f"[模拟运行] 表 {database}.{table} 将删除 {dup_count} 组重复数据",
                            {'columns': use_columns}
                        )

                    # 清理临时表
                    cursor.execute(drop_temp_sql)
                    conn.commit()

                    return (dup_count, affected_rows)

        except Exception as e:
            logger.error(
                f"处理表 {database}.{table} 时出错: {str(e)}",
                {'error_type': type(e).__name__}
            )
            return (0, 0)
        finally:
            self._release_table_lock(database, table)

    def deduplicate_table(
            self,
            database: str,
            table: str,
            columns: Optional[List[str]] = None,
            dry_run: bool = False
    ) -> Tuple[int, int]:
        """
        对指定表进行去重

        :param database: 数据库名
        :param table: 表名
        :param columns: 用于去重的列(为None时使用所有列)
        :param dry_run: 是否模拟运行(只统计不实际删除)
        :return: (重复行数, 删除行数)
        """
        try:
            # 检查表是否存在
            if not self._check_table_exists(database, table):
                logger.warning(f"表 {database}.{table} 不存在，跳过")
                return (0, 0)

            return self._deduplicate_table(database, table, columns, dry_run)
        except Exception as e:
            logger.error(
                f"处理表 {database}.{table} 时发生全局错误: {str(e)}",
                {'error_type': type(e).__name__}
            )
            return (0, 0)

    def deduplicate_database(
            self,
            database: str,
            tables: Optional[List[str]] = None,
            columns_map: Optional[Dict[str, List[str]]] = None,
            dry_run: bool = False,
            parallel: bool = False
    ) -> Dict[str, Tuple[int, int]]:
        """
        对指定数据库的所有表进行去重

        :param database: 数据库名
        :param tables: 要处理的表列表(为None时处理所有表)
        :param columns_map: 各表使用的去重列 {表名: [列名]}
        :param dry_run: 是否模拟运行
        :param parallel: 是否并行处理
        :return: 字典 {表名: (重复行数, 删除行数)}
        """
        results = {}

        try:
            # 检查数据库是否存在
            if not self._check_database_exists(database):
                logger.warning(f"数据库 {database} 不存在，跳过")
                return results

            # 获取要处理的表
            target_tables = tables or self._get_tables(database)
            if not target_tables:
                logger.info(f"数据库 {database} 中没有表，跳过")
                return results

            logger.info(
                f"开始处理数据库 {database} 中的 {len(target_tables)} 张表",
                {'tables': target_tables}
            )

            if parallel and self.max_workers > 1:
                # 并行处理
                with concurrent.futures.ThreadPoolExecutor(
                        max_workers=self.max_workers
                ) as executor:
                    futures = {}
                    for table in target_tables:
                        columns = columns_map.get(table) if columns_map else None
                        futures[executor.submit(
                            self.deduplicate_table,
                            database, table, columns, dry_run
                        )] = table

                    for future in concurrent.futures.as_completed(futures):
                        table = futures[future]
                        try:
                            dup_count, affected_rows = future.result()
                            results[table] = (dup_count, affected_rows)
                        except Exception as e:
                            logger.error(
                                f"处理表 {database}.{table} 时出错: {str(e)}",
                                {'error_type': type(e).__name__}
                            )
                            results[table] = (0, 0)
            else:
                # 串行处理
                for table in target_tables:
                    columns = columns_map.get(table) if columns_map else None
                    dup_count, affected_rows = self.deduplicate_table(
                        database, table, columns, dry_run
                    )
                    results[table] = (dup_count, affected_rows)

            # 统计结果
            total_dup = sum(r[0] for r in results.values())
            total_del = sum(r[1] for r in results.values())

            logger.info(
                f"数据库 {database} 处理完成 - 共发现 {total_dup} 组重复数据，删除 {total_del} 行",
                {'results': results}
            )

            return results

        except Exception as e:
            logger.error(f"处理数据库 {database} 时发生全局错误: {str(e)}", {'error_type': type(e).__name__})
            return results

    def deduplicate_all(
            self,
            databases: Optional[List[str]] = None,
            tables_map: Optional[Dict[str, List[str]]] = None,
            columns_map: Optional[Dict[str, Dict[str, List[str]]]] = None,
            dry_run: bool = False,
            parallel: bool = False
    ) -> Dict[str, Dict[str, Tuple[int, int]]]:
        """
        对所有数据库进行去重

        :param databases: 要处理的数据库列表(为None时处理所有非系统数据库)
        :param tables_map: 各数据库要处理的表 {数据库名: [表名]}
        :param columns_map: 各表使用的去重列 {数据库名: {表名: [列名]}}
        :param dry_run: 是否模拟运行
        :param parallel: 是否并行处理
        :return: 嵌套字典 {数据库名: {表名: (重复行数, 删除行数)}}
        """
        all_results = defaultdict(dict)

        try:
            # 获取要处理的数据库
            target_dbs = databases or self._get_databases()
            if not target_dbs:
                logger.warning("没有可处理的数据库")
                return all_results

            logger.info(f"开始处理 {len(target_dbs)} 个数据库", {'databases': target_dbs})

            if parallel and self.max_workers > 1:
                # 并行处理数据库
                with concurrent.futures.ThreadPoolExecutor(
                        max_workers=self.max_workers
                ) as executor:
                    futures = {}
                    for db in target_dbs:
                        tables = tables_map.get(db) if tables_map else None
                        db_columns_map = columns_map.get(db) if columns_map else None
                        futures[executor.submit(
                            self.deduplicate_database,
                            db, tables, db_columns_map, dry_run, False
                        )] = db

                    for future in concurrent.futures.as_completed(futures):
                        db = futures[future]
                        try:
                            db_results = future.result()
                            all_results[db] = db_results
                        except Exception as e:
                            logger.error(f"处理数据库 {db} 时出错: {str(e)}", {'error_type': type(e).__name__})
                            all_results[db] = {}
            else:
                # 串行处理数据库
                for db in target_dbs:
                    tables = tables_map.get(db) if tables_map else None
                    db_columns_map = columns_map.get(db) if columns_map else None
                    db_results = self.deduplicate_database(
                        db, tables, db_columns_map, dry_run, parallel
                    )
                    all_results[db] = db_results

            # 统计总体结果
            total_dup = sum(
                r[0] for db in all_results.values()
                for r in db.values()
            )
            total_del = sum(
                r[1] for db in all_results.values()
                for r in db.values()
            )

            logger.info(
                f"所有数据库处理完成 - 共发现 {total_dup} 组重复数据，删除 {total_del} 行",
                {'total_results': all_results}
            )

            return all_results

        except Exception as e:
            logger.error(f"全局处理时发生错误: {str(e)}", {'error_type': type(e).__name__})
            return all_results

    @_retry_on_failure
    def _check_database_exists(self, database: str) -> bool:
        """检查数据库是否存在"""
        sql = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s"

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (database,))
                return bool(cursor.fetchone())

    @_retry_on_failure
    def _check_table_exists(self, database: str, table: str) -> bool:
        """检查表是否存在"""
        sql = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (database, table))
                return bool(cursor.fetchone())

    def close(self):
        """关闭连接池"""
        try:
            if hasattr(self, 'pool') and self.pool and not self._closed:
                self.pool.close()
                self._closed = True
                logger.info("数据库连接池已关闭")
        except Exception as e:
            logger.error(f"关闭连接池时出错: {str(e)}", {'error_type': type(e).__name__})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    deduplicator = MySQLDeduplicator(
        username='root',
        password='188988yang188',
        host='localhost',
        port=3306
    )

    # 全库去重(单线程)
    deduplicator.deduplicate_all()

    # # 指定数据库去重(多线程)
    # deduplicator.deduplicate_database('my_db', parallel=True)

    # # 指定表去重(使用特定列)
    # deduplicator.deduplicate_table('my_db', 'my_table', columns=['name', 'date'])

    # 关闭连接
    deduplicator.close()

if __name__ == '__main__':
    main()
