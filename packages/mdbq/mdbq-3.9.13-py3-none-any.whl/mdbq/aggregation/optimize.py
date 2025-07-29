# -*- coding:utf-8 -*-
import pymysql
import logging
from typing import List, Optional, Dict
import time
import re
import os
import hashlib
from dbutils.pooled_db import PooledDB
from mdbq.log import spider_logging
from mdbq.config import config
import threading
import queue

dir_path = os.path.expanduser("~")
config_file = os.path.join(dir_path, 'spd.txt')
my_cont = config.read_config(config_file)
username, password, port = my_cont['username'], my_cont['password'], my_cont['port']
host = '127.0.0.1'
logger = spider_logging.setup_logging(reMoveOldHandler=True, filename='optimize.log')


class MySQLDeduplicator:

    def __init__(self, host: str, username: str, password: str, port: int = 3306):
        self.pool = PooledDB(
            creator=pymysql,
            maxconnections=10,  # 最大连接数
            mincached=2,  # 初始化空闲连接数
            maxcached=5,  # 空闲连接最大缓存数
            blocking=True,
            host=host,
            port=int(port),
            user=username,
            password=password,
            ping=1,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        self.set_typ = {
            '日期': 'date',
            '更新时间': 'timestamp',
        }
        self.tables_to_reset = queue.Queue()  # 线程安全队列
        self.delay_time = 120  # 延迟重置自增 id
        self.lock = threading.Lock()  # 用于关键操作同步

    def get_table_in_databases(self, db_list=None, reset_id=False):
        """
        reset_id: 是否重置自增 id
        """
        if not db_list:
            return
        connection = self.get_connection()
        res = []
        for db_name in db_list:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"USE `{db_name}`")
                    cursor.execute("SHOW TABLES")
                    tables = cursor.fetchall()
                    for index, item in enumerate(tables):
                        res.append(
                            {
                                'db_name': db_name,
                                'table_name': item.get(f'Tables_in_{db_name}', ''),
                                'reset_id': reset_id,
                            }
                        )
            except:
                pass
        connection.close()
        return res

    def deduplicate(
            self,
            tables_list: List[Dict],
            order_column: str = "更新时间",
            order_direction: str = "DESC",
            batch_size: int = 10000,
            id_column: str = "id",
            recent_months: Optional[int] = None
    ) -> bool:
        """
        执行多表去重操作
        :param tables_list: 目标表配置列表，每个元素为字典，包含db_name, table_name, unique_keys（可选）, reset_id（可选）
        :param order_column: 排序字段
        :param order_direction: 排序方向 (ASC/DESC)
        :param batch_size: 批量删除批次大小
        :param id_column: 自增列名称
        :return: 是否全部成功
        """
        if recent_months is not None and (not isinstance(recent_months, int) or recent_months < 1):
            logger.error("recent_months必须为None或正整数")
            return False
        for table_config in tables_list:
            config = {
                'order_column': order_column,
                'order_direction': order_direction,
                'batch_size': batch_size,
                'id_column': id_column,
                'reset_id': table_config.get('reset_id', False),  # 处理默认值
                'unique_keys': table_config.get('unique_keys', None),
                'recent_months': recent_months,
            }
            config.update(table_config)
            self._deduplicate_single_table(**config)

    def _deduplicate_single_table(
            self,
            db_name: str,
            table_name: str,
            unique_keys: Optional[List[str]],
            order_column: str,
            order_direction: str,
            batch_size: int,
            reset_id: bool,
            id_column: str,
            recent_months: Optional[int] = None
    ):
        """单表去重逻辑"""

        # 获取数据库连接并检查有效性
        connection = self.get_connection(db_name=db_name)
        if not connection:
            logger.error(f"连接数据库失败: {db_name}")
            return False

        temp_suffix = hashlib.md5(f"{table_name}{time.time()}".encode()).hexdigest()[:8]
        temp_table = f"temp_{temp_suffix}"

        try:
            # 版本检查在check_db内部
            if not self.check_db(db_name, table_name):
                return False

            with connection.cursor() as cursor:
                # 主键重复检查
                try:
                    cursor.execute(f"""
                        SELECT COUNT(*) AS total, 
                               COUNT(DISTINCT `{id_column}`) AS distinct_count 
                        FROM `{table_name}`
                    """)
                except pymysql.err.InternalError as e:
                    if e.args[0] == pymysql.constants.ER.BAD_FIELD_ERROR:
                        logger.warning(f"{db_name}/{table_name} 跳过主键检查（无{id_column}列）")
                    else:
                        raise
                else:
                    res = cursor.fetchone()
                    if res['total'] != res['distinct_count']:
                        logger.error(f"{db_name}/{table_name} 主键重复: {id_column}")
                        return False

                all_columns = self._get_table_columns(db_name, table_name)
                # 自动生成unique_keys逻辑
                if not unique_keys:
                    exclude_set = {id_column.lower(), order_column.lower()}

                    if not all_columns:
                        logger.error(f"{db_name}/{table_name} 无法获取表列信息")
                        return False

                    # 排除id_column和order_column
                    unique_keys = [
                        col for col in all_columns
                        if col.lower() not in exclude_set
                           and col != id_column  # 额外确保大小写兼容
                           and col != order_column
                    ]
                    # 检查剩余列是否有效
                    if not unique_keys:
                        unique_keys = all_columns
                        logger.warning(f"{db_name}/{table_name} 使用全列作为唯一键: {all_columns}")
                        return False
                    # logger.info(f"自动生成unique_keys: {unique_keys}")
                else:
                    if not self._validate_columns(db_name, table_name, unique_keys):
                        logger.error(f"{db_name}/{table_name} unique_keys中存在无效列名")
                        return False

                # 动态生成临时表名
                partition_clause = ', '.join([f'`{col}`' for col in unique_keys])

                # 使用参数化查询创建临时表
                if self._validate_columns(db_name, table_name, [order_column]):
                    order_clause = f"ORDER BY `{order_column}` {order_direction}" if order_column else ""
                else:
                    order_clause = ''

                # 时间过滤
                where_clause = ""
                query_params = []
                date_column_exists = '日期' in all_columns
                if recent_months and recent_months > 0 and date_column_exists:
                    where_clause = "WHERE `日期` >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)"
                    query_params.append(recent_months)
                elif recent_months and not date_column_exists:
                    logger.warning(f"{db_name}/{table_name} 忽略recent_months参数（无日期列）")

                create_temp_sql = f"""
                            CREATE TEMPORARY TABLE `{temp_table}` AS
                            SELECT tmp_id FROM (
                                SELECT `{id_column}` AS tmp_id,
                                ROW_NUMBER() OVER (
                                    PARTITION BY {partition_clause or '1'}
                                    {order_clause}
                                ) AS row_num
                                FROM `{table_name}`
                                {where_clause}
                            ) t WHERE row_num > 1;
                        """
                cursor.execute(create_temp_sql, query_params)

                logger.info(f'{db_name}/{table_name}  执行排重任务')
                # 批量删除优化
                iteration = 0
                total_deleted = 0
                while True and iteration < 10000:
                    iteration += 1
                    # 获取并删除临时表中的数据，避免重复处理
                    cursor.execute(f"""
                            SELECT tmp_id 
                            FROM `{temp_table}` 
                            LIMIT %s 
                            FOR UPDATE;
                        """, (batch_size,))
                    batch = cursor.fetchall()
                    if not batch:
                        break
                    ids = [str(row['tmp_id']) for row in batch]
                    placeholder = ','.join(['%s'] * len(ids))

                    if ids:
                        try:
                            # 删除主表数据
                            cursor.execute(f"DELETE FROM `{table_name}` WHERE `{id_column}` IN ({placeholder})", ids)

                            # 删除临时表中已处理的记录
                            cursor.execute(f"DELETE FROM `{temp_table}` WHERE tmp_id IN ({placeholder})", ids)
                        except pymysql.err.InternalError as e:
                            if e.args[0] == pymysql.constants.ER.BAD_FIELD_ERROR:
                                logger.error(f"{db_name}/{table_name}  无法通过 {id_column} 删除记录，请检查列存在性")
                                return False
                            raise

                    total_deleted += cursor.rowcount
                    connection.commit()
                    logger.info(f"{db_name}/{table_name}  执行去重, 删除记录数: {total_deleted}")

                if total_deleted > 0:
                    logger.info(f"{db_name}/{table_name}  删除记录数总计: {total_deleted}")

                # 线程安全操作队列
                if reset_id:
                    if not self._validate_columns(db_name, table_name, [id_column]):
                        return True

                    with self.lock:
                        self.tables_to_reset.put((db_name, table_name, id_column))
                    logger.info(f"{db_name}/{table_name} -> {self.delay_time}秒后重置自增id")
                    threading.Timer(self.delay_time, self.delayed_reset_auto_increment).start()

                return True
        except Exception as e:
            logger.error(f"{db_name}/{table_name} 去重操作异常: {e}", exc_info=True)
            connection.rollback()
            return False
        finally:
            with connection.cursor() as cursor:
                cursor.execute(f"DROP TEMPORARY TABLE IF EXISTS `{temp_table}`")
            connection.close()

    def _get_table_columns(self, db_name: str, table_name: str) -> List[str]:
        """获取表的列"""
        try:
            connection = self.get_connection(db_name=db_name)
            with connection.cursor() as cursor:
                cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
                return [row["Field"] for row in cursor.fetchall()]
        except pymysql.Error as e:
            logging.error(f"{db_name}/{table_name} 获取列失败: {e}")
            return []

    def check_db(self, db_name: str, table_name: str) -> bool:
        """数据库检查"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 获取MySQL版本
                    version = self._check_mysql_version(cursor)
                    collation = 'utf8mb4_0900_ai_ci' if version >= 8.0 else 'utf8mb4_general_ci'

                    # 创建数据库
                    cursor.execute(f"""
                        CREATE DATABASE IF NOT EXISTS `{db_name}` 
                        CHARACTER SET utf8mb4 COLLATE {collation}
                    """)
                    conn.commit()

                    # 切换数据库
                    cursor.execute(f"USE `{db_name}`")

                    # 检查表是否存在
                    if not self._table_exists(cursor, table_name):
                        self._create_table(cursor, table_name)
                        conn.commit()
                    return True
        except Exception as e:
            logger.error(f"{db_name}/{table_name} 数据库检查失败: {e}")
            return False

    def get_connection(self, db_name=None):
        """从连接池获取连接"""
        for _ in range(10):
            try:
                if db_name:
                    connection = self.pool.connection()
                    with connection.cursor() as cursor:
                        cursor.execute(f'use {db_name};')
                        return connection

                return self.pool.connection()
            except pymysql.Error as e:
                logger.error(f"{db_name}  获取连接失败: {e}, 30秒后重试...")
                time.sleep(30)
        logger.error(f"{host}: {port}  数据库连接失败，已达最大重试次数")
        return None

    def _validate_identifier(self, name: str) -> bool:
        """更严格的对象名验证（符合MySQL规范）"""
        return re.match(r'^[\w$]+$', name) and len(name) <= 64

    def _validate_columns(self, db_name: str, table_name: str, columns: List[str]) -> bool:
        """验证列是否存在"""
        if not all(self._validate_identifier(col) for col in columns):
            return False
        try:
            connection = self.get_connection(db_name=db_name)
            with connection.cursor() as cursor:
                cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
                existing_columns = {col['Field'] for col in cursor.fetchall()}
                return all(col in existing_columns for col in columns)
        except pymysql.Error as e:
            logging.error(f"{db_name}/{table_name} 列验证失败: {e}")
            return False

    def _check_mysql_version(self, cursor) -> float:
        """通过传入游标检查版本"""
        cursor.execute("SELECT VERSION()")
        return float(cursor.fetchone()['VERSION()'][:3])

    def _table_exists(self, cursor, table_name: str) -> bool:
        cursor.execute("SHOW TABLES LIKE %s", (table_name,))
        return cursor.fetchone() is not None

    def _create_table(self, cursor, table_name: str):
        """安全建表逻辑"""
        columns = ["`id` INT AUTO_INCREMENT PRIMARY KEY"]
        for cn, ct in self.set_typ.items():
            col_def = f"`{cn}` {ct.upper()} NOT NULL DEFAULT "
            if 'INT' in ct:
                col_def += '0'
            elif 'TIMESTAMP' in ct:
                col_def += 'CURRENT_TIMESTAMP'
            else:
                col_def += "''"
            columns.append(col_def)
        cursor.execute(f"""
            CREATE TABLE `{table_name}` (
                {', '.join(columns)}
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

    def delayed_reset_auto_increment(self):
        """线程安全的自增ID重置"""
        while not self.tables_to_reset.empty():
            try:
                item = self.tables_to_reset.get_nowait()
                self._safe_reset_auto_increment(*item)
            except queue.Empty:
                break

    def _safe_reset_auto_increment(self, db_name: str, table_name: str, id_column: str):
        """安全重置自增ID"""
        with self.get_connection(db_name) as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("START TRANSACTION")
                    temp_table = f"reset_{hashlib.md5(table_name.encode()).hexdigest()[:8]}"
                    backup_table = f"{table_name}_backup_{int(time.time())}"
                    cursor.execute(f"CREATE TABLE `{temp_table}` LIKE `{table_name}`")
                    cursor.execute(f"ALTER TABLE `{temp_table}` MODIFY COLUMN `{id_column}` INT NOT NULL")
                    columns = self._get_table_columns(db_name, table_name)
                    if id_column not in columns:
                        logger.error(f"列 {id_column} 不存在于表 {table_name}")
                        return False
                    columns.remove(id_column)
                    columns_str = ', '.join([f'`{col}`' for col in columns])
                    insert_sql = f"""
                        INSERT INTO `{temp_table}` (`{id_column}`, {columns_str})
                        SELECT ROW_NUMBER() OVER (ORDER BY `{id_column}`), {columns_str}
                        FROM `{table_name}` ORDER BY `{id_column}`
                    """
                    cursor.execute(insert_sql)
                    cursor.execute(f"RENAME TABLE `{table_name}` TO `{backup_table}`, `{temp_table}` TO `{table_name}`")
                    cursor.execute(f"ALTER TABLE `{table_name}` MODIFY COLUMN `{id_column}` INT AUTO_INCREMENT")
                    cursor.execute(f"SELECT MAX(`{id_column}`) + 1 AS next_id FROM `{table_name}`")
                    next_id = cursor.fetchone()['next_id'] or 1
                    cursor.execute(f"ALTER TABLE `{table_name}` AUTO_INCREMENT = {next_id}")
                    cursor.execute(f"DROP TABLE IF EXISTS `{backup_table}`")
                    cursor.execute(f"DROP TEMPORARY TABLE IF EXISTS `{temp_table}`")
                    cursor.execute("COMMIT")
                    logger.info(f'{db_name}/{table_name} 已重置自增id')
            except Exception as e:
                logger.error(f"{db_name}/{table_name} 重置自增id失败: {e}")
                cursor.execute("ROLLBACK")
                return False
            finally:
                conn.close()


def main():
    op = MySQLDeduplicator(
        host=host,
        username=username,
        password=password,
        port=port
    )
    op.delay_time = 600
    # tables_list = [
    #     {
    #         'db_name': "测试库",
    #         'table_name': "测试库2",
    #         'reset_id': True,  # 可选, 默认 False
    #         # 'unique_keys': ["日期", "店铺名称", "商品id"]
    #     }
    # ]
    db_list = [
        "京东数据3",
        "属性设置3",
        "推广数据2",
        "推广数据_圣积天猫店",
        "推广数据_淘宝店",
        "推广数据_奥莱店",
        "爱库存2",
        "生意参谋3",
        "生意经3",
        "达摩盘3",
        '人群画像2',
        '商品人群画像2',
        '市场数据3',
        # '数据银行2'
        # '回传数据',
        # '大模型库',
        '安全组',
        # '视频数据',
        # '聚合数据',
    ]
    tables_list = op.get_table_in_databases(db_list=db_list, reset_id=False)
    op.deduplicate(
        order_column = "更新时间",
        order_direction = "DESC",
        batch_size = 1000,
        id_column = "id",
        tables_list=tables_list,
        recent_months=3,
    )
    logger.info(f'全部任务完成')


if __name__ == "__main__":
    main()
