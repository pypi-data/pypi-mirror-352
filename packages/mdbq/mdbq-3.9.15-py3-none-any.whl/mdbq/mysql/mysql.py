# -*- coding:utf-8 -*-
import datetime
import re
import time
from functools import wraps
import warnings
import pymysql
import pandas as pd
from sqlalchemy import create_engine
import os
from mdbq.other import otk
from mdbq.log import mylogger
import json

warnings.filterwarnings('ignore')
"""
建表流程:
建表规范:
"""
logger = mylogger.MyLogger(
    name='mysql',
    logging_mode='both',
    log_level='info',
    log_file='mysql.log',
    log_format='json',
    max_log_size=50,
    backup_count=5,
    enable_async=False,  # 是否启用异步日志
    sample_rate=0.5,  # 采样50%的DEBUG/INFO日志
    sensitive_fields=[],  #  敏感字段列表
)


def count_decimal_places(num_str):
    """ 计算小数位数, 允许科学计数法 """
    match = re.match(r'^[-+]?\d+(\.\d+)?([eE][-+]?\d+)?$', str(num_str))
    if match:
        # 如果是科学计数法
        match = re.findall(r'(\d+)\.(\d+)[eE][-+]?(\d+)$', str(num_str))
        if match:
            if len(match[0]) == 3:
                if int(match[0][2]) < len(match[0][1]):
                    # count_int 清除整数部分开头的 0 并计算整数位数
                    count_int = len(re.sub('^0+', '', str(match[0][0]))) + int(match[0][2])
                    # 计算小数位数
                    count_float = len(match[0][1]) - int(match[0][2])
                    return count_int, count_float
        # 如果是普通小数
        match = re.findall(r'(\d+)\.(\d+)$', str(num_str))
        if match:
            count_int = len(re.sub('^0+', '', str(match[0][0])))
            count_float = len(match[0][1])
            return count_int, count_float  # 计算小数位数
    return 0, 0


class MysqlUpload:
    def __init__(self, username: str, password: str, host: str, port: int, charset: str = 'utf8mb4'):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        if username == '' or password == '' or host == '' or port == 0:
            self.config = None
        else:
            self.config = {
                'host': self.host,
                'port': int(self.port),
                'user': self.username,
                'password': self.password,
                'charset': charset,  # utf8mb4 支持存储四字节的UTF-8字符集
                'cursorclass': pymysql.cursors.DictCursor,
            }
        self.filename = None

    @staticmethod
    def try_except(func):  # 在类内部定义一个异常处理方法

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f'{func.__name__}, {e}')  # 将异常信息返回

        return wrapper

    def keep_connect(self, _db_name, _config, max_try: int=10):
        attempts = 1
        while attempts <= max_try:
            try:
                connection = pymysql.connect(**_config)  # 连接数据库
                return connection
            except Exception as e:
                logger.error(f'{_db_name}: 连接失败，正在重试: {self.host}:{self.port}  {attempts}/{max_try} {e}')
                attempts += 1
                time.sleep(30)
        logger.error(f'{_db_name}: 连接失败，重试次数超限，当前设定次数: {max_try}')
        return None

    def cover_doc_dtypes(self, dict_data):
        """ 清理字典键值 并转换数据类型  """
        if not dict_data:
            logger.info(f'mysql.py -> MysqlUpload -> cover_dict_dtypes -> 传入的字典不能为空')
            return
        __res_dict = {}
        new_dict_data = {}
        for k, v in dict_data.items():
            k = str(k).lower()
            k = re.sub(r'[()\-，,$&~^、 （）\"\'“”=·/。》《><！!`]', '_', k, re.IGNORECASE)
            k = k.replace('）', '')
            k = re.sub(r'_{2,}', '_', k)
            k = re.sub(r'_+$', '', k)
            result1 = re.findall(r'编码|_?id|货号|款号|文件大小', k, re.IGNORECASE)
            result2 = re.findall(r'占比$|投产$|产出$|roi$|率$', k, re.IGNORECASE)
            result3 = re.findall(r'同比$|环比$', k, re.IGNORECASE)
            result4 = re.findall(r'花费$|消耗$|金额$', k, re.IGNORECASE)

            date_type = otk.is_valid_date(v)  # 判断日期时间
            int_num = otk.is_integer(v)  # 判断整数
            count_int, count_float = count_decimal_places(v)  # 判断小数，返回小数位数
            if result1:  # 京东sku/spu商品信息
                __res_dict.update({k: 'varchar(100)'})
            elif k == '日期':
                __res_dict.update({k: 'DATE'})
            elif k == '更新时间':
                __res_dict.update({k: 'TIMESTAMP'})
            elif result2:  # 小数
                __res_dict.update({k: 'decimal(10,4)'})
            elif date_type == 1:  # 纯日期
                __res_dict.update({k: 'DATE'})
            elif date_type == 2:  # 日期+时间
                __res_dict.update({k: 'DATETIME'})
            elif int_num:
                __res_dict.update({k: 'INT'})
            elif count_float > 0:
                if count_int + count_float > 10:
                    if count_float >= 6:
                        __res_dict.update({k: 'decimal(14,6)'})
                    else:
                        __res_dict.update({k: 'decimal(14,4)'})
                elif count_float >= 6:
                    __res_dict.update({k: 'decimal(14,6)'})
                elif count_float >= 4:
                    __res_dict.update({k: 'decimal(12,4)'})
                else:
                    __res_dict.update({k: 'decimal(10,2)'})
            else:
                __res_dict.update({k: 'varchar(255)'})
            new_dict_data.update({k: v})
        __res_dict.update({'数据主体': 'longblob'})
        return __res_dict, new_dict_data

    @try_except
    def insert_many_dict(self, db_name, table_name, dict_data_list, icm_update=None, index_length=100, set_typ=None, allow_not_null=False, cut_data=None):
        """
        插入字典数据
        dict_data： 字典
        index_length: 索引长度
        icm_update: 增量更正
        set_typ: {}
        allow_not_null: 创建允许插入空值的列，正常情况下不允许空值
        """
        if not self.config:
            return

        if not dict_data_list:
            logger.info(f'dict_data_list 不能为空 ')
            return
        dict_data = dict_data_list[0]
        if cut_data:
            if '日期' in dict_data.keys():
                try:
                    __y = pd.to_datetime(dict_data['日期']).strftime('%Y')
                    __y_m = pd.to_datetime(dict_data['日期']).strftime('%Y-%m')
                    if str(cut_data).lower() == 'year':
                        table_name = f'{table_name}_{__y}'
                    elif str(cut_data).lower() == 'month':
                        table_name = f'{table_name}_{__y_m}'
                    else:
                        logger.info(f'参数不正确，cut_data应为 year 或 month ')
                except Exception as e:
                    logger.error(f'{table_name} 将数据按年/月保存(cut_data)，但在转换日期时报错 -> {e}')

        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")  # 检查数据库是否存在
            database_exists = cursor.fetchone()
            if not database_exists:
                # 如果数据库不存在，则新建
                sql = f"CREATE DATABASE `{db_name}` COLLATE utf8mb4_0900_ai_ci"
                cursor.execute(sql)
                connection.commit()
                logger.info(f"创建Database: {db_name}")

        self.config.update({'database': db_name})  # 添加更新 config 字段
        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            # 1. 查询表, 不存在则创建一个空表
            sql = "SHOW TABLES LIKE %s;"  # 有特殊字符不需转义
            cursor.execute(sql, (table_name,))
            if not cursor.fetchone():
                sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (id INT AUTO_INCREMENT PRIMARY KEY);"
                cursor.execute(sql)
                logger.info(f'创建 mysql 表: {table_name}')

            # 根据 dict_data 的值添加指定的数据类型
            dtypes, dict_data = self.cover_dict_dtypes(dict_data=dict_data)  # {'店铺名称': 'varchar(100)',...}
            if set_typ:
                # 更新自定义的列数据类型
                for k, v in dtypes.copy().items():
                    # 确保传进来的 set_typ 键存在于实际的 df 列才 update
                    [dtypes.update({k: inside_v}) for inside_k, inside_v in set_typ.items() if k == inside_k]

            # 检查列
            sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;"
            cursor.execute(sql, (db_name, table_name))
            col_exist = [item['COLUMN_NAME'] for item in cursor.fetchall()]  # 已存在的所有列
            col_not_exist = [col for col in dict_data.keys() if col not in col_exist]  # 不存在的列
            # 不存在则新建列
            if col_not_exist:  # 数据表中不存在的列
                for col in col_not_exist:
                    #  创建列，需转义
                    if allow_not_null:
                        sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {dtypes[col]};"
                    else:
                        sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {dtypes[col]} NOT NULL;"

                    cursor.execute(sql)
                    logger.info(f"添加列: {col}({dtypes[col]})")  # 添加列并指定数据类型

                    if col == '日期':
                        sql = f"CREATE INDEX index_name ON `{table_name}`(`{col}`);"
                        logger.info(f"设置为索引: {col}({dtypes[col]})")
                        cursor.execute(sql)

            connection.commit()  # 提交事务
            """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            # 处理插入的数据
            for dict_data in dict_data_list:
                dtypes, dict_data = self.cover_dict_dtypes(dict_data=dict_data)  # {'店铺名称': 'varchar(100)',...}
                if icm_update:
                    """ 使用增量更新: 需确保 icm_update['主键'] 传进来的列组合是数据表中唯一，值不会发生变化且不会重复，否则可能产生覆盖 """
                    sql = 'SELECT COLUMN_NAME FROM information_schema.columns WHERE table_schema = %s AND table_name = %s'
                    cursor.execute(sql, (db_name, table_name))
                    columns = cursor.fetchall()
                    cols_exist = [col['COLUMN_NAME'] for col in columns]  # 数据表的所有列, 返回 list
                    # 保留原始列名，不提前转义
                    raw_update_col = [item for item in cols_exist if item not in icm_update and item != 'id']  # 除了主键外的其他列

                    # 构建条件参数（使用原始列名）
                    condition_params = []
                    condition_parts = []
                    for up_col in icm_update:
                        condition_parts.append(f"`{up_col}` = %s")  # SQL 转义
                        condition_params.append(dict_data[up_col])  # 原始列名用于访问数据

                    # 动态转义列名生成 SQL 查询字段
                    escaped_update_col = [f'`{col}`' for col in raw_update_col]
                    sql = f"""SELECT {','.join(escaped_update_col)} FROM `{table_name}` WHERE {' AND '.join(condition_parts)}"""
                    cursor.execute(sql, condition_params)
                    results = cursor.fetchall()

                    if results:
                        for result in results:
                            change_col = []
                            change_placeholders = []
                            set_params = []
                            for raw_col in raw_update_col:
                                # 使用原始列名访问数据
                                df_value = str(dict_data[raw_col])
                                mysql_value = str(result[raw_col])

                                # 清理小数点后多余的零
                                if '.' in df_value:
                                    df_value = re.sub(r'0+$', '', df_value).rstrip('.')
                                if '.' in mysql_value:
                                    mysql_value = re.sub(r'0+$', '', mysql_value).rstrip('.')

                                if df_value != mysql_value:
                                    change_placeholders.append(f"`{raw_col}` = %s")  # 动态转义列名
                                    set_params.append(dict_data[raw_col])
                                    change_col.append(raw_col)

                            if change_placeholders:
                                full_params = set_params + condition_params
                                sql = f"""UPDATE `{table_name}` 
                                             SET {','.join(change_placeholders)} 
                                             WHERE {' AND '.join(condition_parts)}"""
                                cursor.execute(sql, full_params)
                    else:  # 没有数据返回，则直接插入数据
                        # 参数化插入
                        cols = ', '.join([f'`{k}`' for k in dict_data.keys()])
                        placeholders = ', '.join(['%s'] * len(dict_data))
                        sql = f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})"
                        cursor.execute(sql, tuple(dict_data.values()))
                    connection.commit()  # 提交数据库
                    continue

                # 标准插入逻辑（参数化修改）
                # 构造更新列（排除主键）
                update_cols = [k for k in dict_data.keys()]
                # 构建SQL
                cols = ', '.join([f'`{k}`' for k in dict_data.keys()])
                placeholders = ', '.join(['%s'] * len(dict_data))
                update_clause = ', '.join([f'`{k}` = VALUES(`{k}`)' for k in update_cols]) or 'id=id'

                sql = f"""INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_clause}"""
                # 执行参数化查询
                try:
                    cursor.execute(sql, tuple(dict_data.values()))
                    connection.commit()
                except pymysql.Error as e:
                    logger.error(f"插入失败: {e}\nSQL: {cursor.mogrify(sql, tuple(dict_data.values()))}")
                    connection.rollback()
        connection.close()

    # @try_except
    def dict_to_mysql(self, db_name, table_name, dict_data, icm_update=None, index_length=100, set_typ=None, allow_not_null=False, cut_data=None):
        """
        插入字典数据
        dict_data： 字典
        index_length: 索引长度
        icm_update: 增量更新
        set_typ: {}
        allow_not_null: 创建允许插入空值的列，正常情况下不允许空值
        """
        if not self.config:
            return

        if cut_data:
            if '日期' in dict_data.keys():
                try:
                    __y = pd.to_datetime(dict_data['日期']).strftime('%Y')
                    __y_m = pd.to_datetime(dict_data['日期']).strftime('%Y-%m')
                    if str(cut_data).lower() == 'year':
                        table_name = f'{table_name}_{__y}'
                    elif str(cut_data).lower() == 'month':
                        table_name = f'{table_name}_{__y_m}'
                    else:
                        logger.info(f'参数不正确，cut_data应为 year 或 month ')
                except Exception as e:
                    logger.error(f'{table_name} 将数据按年/月保存(cut_data)，但在转换日期时报错 -> {e}')

        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")  # 检查数据库是否存在
            database_exists = cursor.fetchone()
            if not database_exists:
                # 如果数据库不存在，则新建
                sql = f"CREATE DATABASE `{db_name}` COLLATE utf8mb4_0900_ai_ci"
                cursor.execute(sql)
                connection.commit()
                logger.info(f"创建Database: {db_name}")

        self.config.update({'database': db_name})  # 添加更新 config 字段
        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            # 1. 查询表, 不存在则创建一个空表
            sql = "SHOW TABLES LIKE %s;"  # 有特殊字符不需转义
            cursor.execute(sql, (table_name,))
            if not cursor.fetchone():
                sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (id INT AUTO_INCREMENT PRIMARY KEY);"
                cursor.execute(sql)
                logger.info(f'创建 mysql 表: {table_name}')

            # 根据 dict_data 的值添加指定的数据类型
            dtypes, dict_data = self.cover_dict_dtypes(dict_data=dict_data)  # {'店铺名称': 'varchar(100)',...}
            if set_typ:
                # 更新自定义的列数据类型
                for k, v in dtypes.copy().items():
                    # 确保传进来的 set_typ 键存在于实际的 df 列才 update
                    [dtypes.update({k: inside_v}) for inside_k, inside_v in set_typ.items() if k == inside_k]

            # 检查列
            sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;"
            cursor.execute(sql, (db_name, table_name))
            col_exist = [item['COLUMN_NAME'] for item in cursor.fetchall()]  # 已存在的所有列
            col_not_exist = [col for col in dict_data.keys() if col not in col_exist]  # 不存在的列
            # 不存在则新建列
            if col_not_exist:  # 数据表中不存在的列
                for col in col_not_exist:
                    #  创建列，需转义
                    if allow_not_null:
                        sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {dtypes[col]};"
                    else:
                        sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {dtypes[col]} NOT NULL;"
                    cursor.execute(sql)
                    logger.info(f"添加列: {col}({dtypes[col]})")  # 添加列并指定数据类型

                    if col == '日期':
                        sql = f"CREATE INDEX index_name ON `{table_name}`(`{col}`);"
                        logger.info(f"设置为索引: {col}({dtypes[col]})")
                        cursor.execute(sql)
            connection.commit()  # 提交事务
            """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            # 处理插入的数据
            if icm_update:
                """ 使用增量更新: 需确保 icm_update['主键'] 传进来的列组合是数据表中唯一，值不会发生变化且不会重复，否则可能产生覆盖 """
                sql = """SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s"""
                cursor.execute(sql, (db_name, table_name))
                cols_exist = [col['COLUMN_NAME'] for col in cursor.fetchall()] # 数据表的所有列, 返回 list

                # 保留原始列名，不提前转义
                raw_update_col = [item for item in cols_exist if item not in icm_update and item != 'id']

                # 构建条件参数（使用原始列名）
                condition_params = []
                condition_parts = []
                for up_col in icm_update:
                    condition_parts.append(f"`{up_col}` = %s")  # SQL 转义
                    condition_params.append(dict_data[up_col])  # 原始列名访问数据

                # 动态转义列名生成 SQL 查询字段
                escaped_update_col = [f'`{col}`' for col in raw_update_col]
                sql = f"""SELECT {','.join(escaped_update_col)} FROM `{table_name}` WHERE {' AND '.join(condition_parts)}"""
                cursor.execute(sql, condition_params)
                results = cursor.fetchall()

                if results:
                    for result in results:
                        change_col = []
                        change_placeholders = []
                        set_params = []
                        for raw_col in raw_update_col:
                            # 使用原始列名访问数据
                            df_value = str(dict_data[raw_col])
                            mysql_value = str(result[raw_col])

                            # 清理小数点后多余的零
                            if '.' in df_value:
                                df_value = re.sub(r'0+$', '', df_value).rstrip('.')
                            if '.' in mysql_value:
                                mysql_value = re.sub(r'0+$', '', mysql_value).rstrip('.')

                            if df_value != mysql_value:
                                change_placeholders.append(f"`{raw_col}` = %s")  # 动态转义列名
                                set_params.append(dict_data[raw_col])
                                change_col.append(raw_col)

                        if change_placeholders:
                            full_params = set_params + condition_params
                            sql = f"""UPDATE `{table_name}` 
                                         SET {','.join(change_placeholders)} 
                                         WHERE {' AND '.join(condition_parts)}"""
                            cursor.execute(sql, full_params)
                else:  # 没有数据返回，则直接插入数据
                    # 参数化插入语句
                    keys = [f"`{k}`" for k in dict_data.keys()]
                    placeholders = ','.join(['%s'] * len(dict_data))
                    update_clause = ','.join([f"`{k}`=VALUES(`{k}`)" for k in dict_data.keys()])
                    sql = f"""INSERT INTO `{table_name}` ({','.join(keys)}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_clause}"""
                    cursor.execute(sql, tuple(dict_data.values()))
                connection.commit()  # 提交数据库
                connection.close()
                return

            # 常规插入处理（参数化）
            keys = [f"`{k}`" for k in dict_data.keys()]
            placeholders = ','.join(['%s'] * len(dict_data))
            update_clause = ','.join([f"`{k}`=VALUES(`{k}`)" for k in dict_data.keys()])
            sql = f"""INSERT INTO `{table_name}` ({','.join(keys)}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_clause}"""
            cursor.execute(sql, tuple(dict_data.values()))
            connection.commit()
        connection.close()

    def cover_dict_dtypes(self, dict_data):
        """ 清理字典键值 并转换数据类型  """
        if not dict_data:
            logger.info(f'mysql.py -> MysqlUpload -> cover_dict_dtypes -> 传入的字典不能为空')
            return
        __res_dict = {}
        new_dict_data = {}
        for k, v in dict_data.items():
            k = str(k).lower()
            k = re.sub(r'[()\-，,$&~^、 （）\"\'“”=·/。》《><！!`]', '_', k, re.IGNORECASE)
            k = k.replace('）', '')
            k = re.sub(r'_{2,}', '_', k)
            k = re.sub(r'_+$', '', k)
            if str(v) == '':
                v = 0
            v = str(v)
            v = re.sub('^="|"$', '', v, re.I)
            v = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(v))  # 移除控制字符
            if re.findall(r'^[-+]?\d+\.?\d*%$', v):
                v = str(float(v.rstrip("%")) / 100)

            result1 = re.findall(r'编码|_?id|货号|款号|文件大小', k, re.IGNORECASE)
            result2 = re.findall(r'占比$|投产$|产出$|roi$|率$', k, re.IGNORECASE)
            result3 = re.findall(r'同比$|环比$', k, re.IGNORECASE)
            result4 = re.findall(r'花费$|消耗$|金额$', k, re.IGNORECASE)

            date_type = otk.is_valid_date(v)  # 判断日期时间
            int_num = otk.is_integer(v)  # 判断整数
            count_int, count_float = count_decimal_places(v)  # 判断小数，返回小数位数
            if result1:  # 京东sku/spu商品信息
                __res_dict.update({k: 'varchar(100)'})
            elif k == '日期':
                __res_dict.update({k: 'DATE'})
            elif k == '更新时间':
                __res_dict.update({k: 'TIMESTAMP'})
            elif result2:  # 小数
                __res_dict.update({k: 'decimal(10,4)'})
            elif date_type == 1:  # 纯日期
                __res_dict.update({k: 'DATE'})
            elif date_type == 2:  # 日期+时间
                __res_dict.update({k: 'DATETIME'})
            elif int_num:
                __res_dict.update({k: 'INT'})
            elif count_float > 0:
                if count_int + count_float > 10:
                    # if count_float > 5:
                    #     v = round(float(v), 4)
                    if count_float >= 6:
                        __res_dict.update({k: 'decimal(14,6)'})
                    else:
                        __res_dict.update({k: 'decimal(14,4)'})
                elif count_float >= 6:
                    __res_dict.update({k: 'decimal(14,6)'})
                elif count_float >= 4:
                    __res_dict.update({k: 'decimal(12,4)'})
                else:
                    __res_dict.update({k: 'decimal(10,2)'})
            else:
                __res_dict.update({k: 'varchar(255)'})
            new_dict_data.update({k: v})
        return __res_dict, new_dict_data

    def convert_df_dtypes(self, df: pd.DataFrame):
        """ 清理 df 的值和列名，并转换数据类型 """
        df = otk.cover_df(df=df)  # 清理 df 的值和列名
        [pd.to_numeric(df[col], errors='ignore') for col in df.columns.tolist()]
        dtypes = df.dtypes.to_dict()
        __res_dict = {}
        for k, v in dtypes.copy().items():
            result1 = re.findall(r'编码|_?id|货号|款号|文件大小', k, re.IGNORECASE)
            result2 = re.findall(r'占比$|投产$|产出$|roi$|率$', k, re.IGNORECASE)
            result3 = re.findall(r'同比$|环比$', k, re.IGNORECASE)
            result4 = re.findall(r'花费$|消耗$|金额$', k, re.IGNORECASE)

            if result1:  # id/sku/spu商品信息
                __res_dict.update({k: 'varchar(50)'})
            elif result2:  # 小数
                __res_dict.update({k: 'decimal(10,4)'})
            elif result3:  # 小数
                __res_dict.update({k: 'decimal(12,4)'})
            elif result4:  # 小数
                __res_dict.update({k: 'decimal(12,2)'})
            elif k == '日期':
                __res_dict.update({k: 'date'})
            elif k == '更新时间':
                __res_dict.update({k: 'timestamp'})
            elif v == 'int64':
                __res_dict.update({k: 'int'})
            elif v == 'float64':
                __res_dict.update({k: 'decimal(10,4)'})
            elif v == 'bool':
                __res_dict.update({k: 'boolean'})
            elif v == 'datetime64[ns]':
                __res_dict.update({k: 'datetime'})
            else:
                __res_dict.update({k: 'varchar(255)'})
        return __res_dict, df

    @try_except
    def df_to_mysql(self, df, db_name, table_name, set_typ=None, icm_update=[], move_insert=False, df_sql=False,
                    filename=None, count=None, allow_not_null=False, cut_data=None):
        """
        db_name: 数据库名
        table_name: 表名
        move_insert: 根据df 的日期，先移除数据库数据，再插入, df_sql, icm_update 都要设置为 False
        原则上只限于聚合数据使用，原始数据插入时不要设置
        df_sql: 这是一个临时参数, 值为 True 时使用 df.to_sql 函数上传整个表, 不会排重，初创表大量上传数据的时候使用
        icm_update: 增量更新, 在聚合数据中使用，原始文件不要使用
                使用增量更新: 必须确保 icm_update 传进来的列必须是数据表中唯一主键，值不会发生变化，不会重复，否则可能产生错乱覆盖情况
        filename: 用来追踪处理进度，传这个参数是方便定位产生错误的文件
        allow_not_null: 创建允许插入空值的列，正常情况下不允许空值
        """
        if not self.config:
            return
        if icm_update:
            if move_insert or df_sql:
                logger.info(f'icm_update/move_insert/df_sql 参数不能同时设定')
                return
        if move_insert:
            if icm_update or df_sql:
                logger.info(f'icm_update/move_insert/df_sql 参数不能同时设定')
                return

        self.filename = filename
        if isinstance(df, pd.DataFrame):
            if len(df) == 0:
                logger.info(f'{db_name}: {table_name} 传入的 df 数据长度为0, {self.filename}')
                return
        else:
            logger.info(f'{db_name}: {table_name} 传入的 df 不是有效的 dataframe 结构, {self.filename}')
            return
        if not db_name or db_name == 'None':
            logger.info(f'{db_name} 不能为 None')
            return

        if cut_data:
            if '日期' in df.columns.tolist():
                try:
                    df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d', errors='ignore')
                    min_year = df['日期'].min(skipna=True).year
                    min_month = df['日期'].min(skipna=True).month
                    if 0 < int(min_month) < 10 and not str(min_month).startswith('0'):
                        min_month = f'0{min_month}'
                    if str(cut_data).lower() == 'year':
                        table_name = f'{table_name}_{min_year}'
                    elif str(cut_data).lower() == 'month':
                        table_name = f'{table_name}_{min_year}_{min_month}'
                    else:
                        logger.info(f'参数不正确，cut_data应为 year 或 month ')
                except Exception as e:
                    logger.error(f'{table_name} 将数据按年/月保存(cut_data)，但在转换日期时报错 -> {e}')
        # 清理 dataframe 非法值，并转换获取数据类型
        dtypes, df = self.convert_df_dtypes(df)
        if set_typ:
            # 更新自定义的列数据类型
            for k, v in dtypes.copy().items():
                # 确保传进来的 set_typ 键存在于实际的 df 列才 update
                [dtypes.update({k: inside_v}) for inside_k, inside_v in set_typ.items() if k == inside_k]

        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES LIKE %s", (db_name,))  # 检查数据库是否存在
            database_exists = cursor.fetchone()
            if not database_exists:
                # 如果数据库不存在，则新建
                sql = f"CREATE DATABASE `{db_name}` COLLATE utf8mb4_0900_ai_ci"
                cursor.execute(sql)
                connection.commit()
                logger.info(f"创建Database: {db_name}")

        self.config.update({'database': db_name})  # 添加更新 config 字段
        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            # 1. 查询表, 不存在则创建一个空表
            sql = "SHOW TABLES LIKE %s;"  # 有特殊字符不需转义
            cursor.execute(sql, (table_name,))
            if not cursor.fetchone():
                create_table_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (id INT AUTO_INCREMENT PRIMARY KEY)"
                cursor.execute(create_table_sql)
                logger.info(f'创建 mysql 表: {table_name}')

            #  有特殊字符不需转义
            sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;"
            cursor.execute(sql, (db_name, table_name))
            col_exist = [item['COLUMN_NAME'] for item in cursor.fetchall()]
            cols = df.columns.tolist()
            col_not_exist = [col for col in cols if col not in col_exist]

            # 检查列，不存在则新建列
            if col_not_exist:  # 数据表中不存在的列
                for col in col_not_exist:
                    #  创建列，需转义
                    alter_sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {dtypes[col]}"
                    if not allow_not_null:
                        alter_sql += " NOT NULL"
                    cursor.execute(alter_sql)
                    logger.info(f"添加列: {col}({dtypes[col]})")  # 添加列并指定数据类型

                    # 创建索引
                    if col == '日期':
                        sql = f"SHOW INDEXES FROM `{table_name}` WHERE `Column_name` = %s"
                        cursor.execute(sql, (col,))
                        result = cursor.fetchone()  # 检查索引是否存在
                        if not result:
                            cursor.execute(f"CREATE INDEX index_name ON `{table_name}`(`{col}`)")
            connection.commit()  # 提交事务

            if df_sql:
                logger.info(f'正在更新: mysql ({self.host}:{self.port}) {db_name}/{table_name}, {count}, {self.filename}')
                engine = create_engine(
                    f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{db_name}")  # 创建数据库引擎
                df.to_sql(
                    name=table_name,
                    con=engine,
                    if_exists='append',
                    index=False,
                    chunksize=1000,
                    method='multi'
                )
                connection.commit()  # 提交事务
                connection.close()
                return

            # 5. 移除指定日期范围内的数据，原则上只限于聚合数据使用，原始数据插入时不要设置
            if move_insert and '日期' in df.columns.tolist():
                # 移除数据
                dates = df['日期'].values.tolist()
                dates = [pd.to_datetime(item) for item in dates]  # 需要先转换类型才能用 min, max
                start_date = pd.to_datetime(min(dates)).strftime('%Y-%m-%d')
                end_date = (pd.to_datetime(max(dates)) + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

                delete_sql = f"""
                                DELETE FROM `{table_name}` 
                                WHERE 日期 BETWEEN %s AND %s
                            """
                cursor.execute(delete_sql, (start_date, end_date))
                connection.commit()

                # 插入数据
                engine = create_engine(
                    f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{db_name}")  # 创建数据库引擎
                df.to_sql(
                    name=table_name,
                    con=engine,
                    if_exists='append',
                    index=False,
                    chunksize=1000,
                    method='multi'
                )
                return

            datas = df.to_dict(orient='records')
            for data in datas:
                # data 是传进来待处理的数据, 不是数据库数据
                # data 示例: {'日期': Timestamp('2024-08-27 00:00:00'), '推广费余额': 33299, '品销宝余额': 2930.73, '短信剩余': 67471}
                try:
                    # 预处理数据：转换非字符串类型
                    processed_data = {}
                    for k, v in data.items():
                        if isinstance(v, (int, float)):
                            processed_data[k] = float(v)
                        elif isinstance(v, pd.Timestamp):
                            processed_data[k] = v.strftime('%Y-%m-%d')
                        else:
                            processed_data[k] = str(v)

                    # 构建基础SQL要素
                    columns = [f'`{k}`' for k in processed_data.keys()]
                    placeholders = ', '.join(['%s'] * len(processed_data))
                    values = list(processed_data.values())

                    # 构建基本INSERT语句
                    insert_sql = f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ({placeholders})"

                    if icm_update:  # 增量更新, 专门用于聚合数据，其他库不要调用
                        # 获取数据表结构
                        cursor.execute(
                            "SELECT COLUMN_NAME FROM information_schema.columns "
                            "WHERE table_schema = %s AND table_name = %s",
                            (db_name, table_name)
                        )
                        cols_exist = [row['COLUMN_NAME'] for row in cursor.fetchall()]
                        update_columns = [col for col in cols_exist if col not in icm_update and col != 'id']

                        # 构建WHERE条件
                        where_conditions = []
                        where_values = []
                        for col in icm_update:
                            where_conditions.append(f"`{col}` = %s")
                            where_values.append(processed_data[col])

                        # 查询现有数据
                        select_sql = f"SELECT {', '.join([f'`{col}`' for col in update_columns])} " \
                                     f"FROM `{table_name}` WHERE {' AND '.join(where_conditions)}"
                        cursor.execute(select_sql, where_values)
                        existing_data = cursor.fetchone()

                        if existing_data:
                            # 比较并构建更新语句
                            update_set = []
                            update_values = []
                            for col in update_columns:
                                db_value = existing_data[col]
                                new_value = processed_data[col]

                                # 处理数值类型的精度差异
                                if isinstance(db_value, float) and isinstance(new_value, float):
                                    if not math.isclose(db_value, new_value, rel_tol=1e-9):
                                        update_set.append(f"`{col}` = %s")
                                        update_values.append(new_value)
                                elif db_value != new_value:
                                    update_set.append(f"`{col}` = %s")
                                    update_values.append(new_value)

                            if update_set:
                                update_sql = f"UPDATE `{table_name}` SET {', '.join(update_set)} " \
                                             f"WHERE {' AND '.join(where_conditions)}"
                                cursor.execute(update_sql, update_values + where_values)
                        else:
                            cursor.execute(insert_sql, values)
                    else:
                        # 普通插入
                        cursor.execute(insert_sql, values)
                except Exception as e:
                    pass
        connection.commit()  # 提交事务
        connection.close()


class OptimizeDatas:
    """
    数据维护 删除 mysql 的冗余数据
    更新过程:
    1. 读取所有数据表
    2. 遍历表, 遍历列, 如果存在日期列则按天遍历所有日期, 不存在则全表读取
    3. 按天删除所有冗余数据(存在日期列时)
    tips: 查找冗余数据的方式是创建一个临时迭代器, 逐行读取数据并添加到迭代器, 出现重复时将重复数据的 id 添加到临时列表, 按列表 id 执行删除
    """
    def __init__(self, username: str, password: str, host: str, port: int, charset: str = 'utf8mb4'):
        self.username = username
        self.password = password
        self.host = host
        self.port = port  # 默认端口, 此后可能更新，不作为必传参数
        self.charset = charset
        self.config = {
            'host': self.host,
            'port': int(self.port),
            'user': self.username,
            'password': self.password,
            'charset': self.charset,  # utf8mb4 支持存储四字节的UTF-8字符集
            'cursorclass': pymysql.cursors.DictCursor,
        }
        self.db_name_lists: list = []  # 更新多个数据库 删除重复数据
        self.db_name = None
        self.days: int = 63  # 对近 N 天的数据进行排重
        self.end_date = None
        self.start_date = None
        self.connection = None

    @staticmethod
    def try_except(func):  # 在类内部定义一个异常处理方法

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f'{func.__name__}, {e}')  # 将异常信息返回

        return wrapper

    def keep_connect(self, _db_name, _config, max_try: int=10):
        attempts = 1
        while attempts <= max_try:
            try:
                connection = pymysql.connect(**_config)  # 连接数据库
                return connection
            except Exception as e:
                logger.error(f'{_db_name}连接失败，正在重试: {self.host}:{self.port}  {attempts}/{max_try} {e}')
                attempts += 1
                time.sleep(30)
        logger.error(f'{_db_name}: 连接失败，重试次数超限，当前设定次数: {max_try}')
        return None

    def optimize_list(self):
        """
        更新多个数据库 移除冗余数据
        需要设置 self.db_name_lists
        """
        if not self.db_name_lists:
            logger.info(f'尚未设置参数: self.db_name_lists')
            return
        for db_name in self.db_name_lists:
            self.db_name = db_name
            self.optimize()

    def optimize(self, except_key=['更新时间']):
        """ 更新一个数据库 移除冗余数据 """
        if not self.db_name:
            logger.info(f'尚未设置参数: self.db_name')
            return
        tables = self.table_list(db_name=self.db_name)
        if not tables:
            logger.info(f'{self.db_name} -> 数据表不存在')
            return

        # 日期初始化
        if not self.end_date:
            self.end_date = pd.to_datetime(datetime.datetime.today())
        else:
            self.end_date = pd.to_datetime(self.end_date)
        if self.days:
            self.start_date = pd.to_datetime(self.end_date - datetime.timedelta(days=self.days))
        if not self.start_date:
            self.start_date = self.end_date
        else:
            self.start_date = pd.to_datetime(self.start_date)
        start_date_before = self.start_date
        end_date_before = self.end_date

        logger.info(f'mysql({self.host}: {self.port}) {self.db_name} 数据库优化中(日期长度: {self.days} 天)...')
        for table_dict in tables:
            for key, table_name in table_dict.items():
                self.config.update({'database': self.db_name})  # 添加更新 config 字段
                self.connection = self.keep_connect(_db_name=self.db_name, _config=self.config, max_try=10)
                if not self.connection:
                    return
                with self.connection.cursor() as cursor:
                    sql = f"SELECT 1 FROM `{table_name}` LIMIT 1"
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    if not result:
                        logger.info(f'数据表: {table_name}, 数据长度为 0')
                        continue  # 检查数据表是否为空

                    cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")  # 查询数据表的列信息
                    columns = cursor.fetchall()
                    date_exist = False
                    for col in columns:  # 遍历列信息，检查是否存在类型为日期的列
                        if col['Field'] == '日期' and (col['Type'] == 'date' or col['Type'].startswith('datetime')):
                            date_exist = True
                            break
                    if date_exist:  # 存在日期列
                        sql_max = f"SELECT MAX(日期) AS max_date FROM `{table_name}`"
                        sql_min = f"SELECT MIN(日期) AS min_date FROM `{table_name}`"
                        cursor.execute(sql_max)
                        max_result = cursor.fetchone()
                        cursor.execute(sql_min)
                        min_result = cursor.fetchone()
                        # 匹配修改为合适的起始和结束日期
                        if self.start_date < pd.to_datetime(min_result['min_date']):
                            self.start_date = pd.to_datetime(min_result['min_date'])
                        if self.end_date > pd.to_datetime(max_result['max_date']):
                            self.end_date = pd.to_datetime(max_result['max_date'])
                        dates_list = self.day_list(start_date=self.start_date, end_date=self.end_date)
                        # dates_list 是日期列表
                        for date in dates_list:
                            self.delete_duplicate(table_name=table_name, date=date, except_key=except_key)
                        self.start_date = start_date_before  # 重置，不然日期错乱
                        self.end_date = end_date_before
                    else:  # 不存在日期列的情况
                        self.delete_duplicate2(table_name=table_name, except_key=except_key)
                self.connection.close()
        logger.info(f'mysql({self.host}: {self.port}) {self.db_name} 数据库优化完成!')

    def delete_duplicate(self, table_name, date, except_key=['更新时间']):
        datas = self.table_datas(db_name=self.db_name, table_name=str(table_name), date=date)
        if not datas:
            return
        duplicate_id = []  # 出现重复的 id
        all_datas = []  # 迭代器
        for data in datas:
            for e_key in except_key:
                if e_key in data.keys():  # 在检查重复数据时，不包含 更新时间 字段
                    del data[e_key]
            try:
                delete_id = data['id']
                del data['id']
                data = re.sub(r'\.0+\', ', '\', ', str(data))  # 统一移除小数点后面的 0
                if data in all_datas:  # 数据出现重复时
                    if delete_id:
                        duplicate_id.append(delete_id)  # 添加 id 到 duplicate_id
                        continue
                all_datas.append(data)  # 数据没有重复
            except Exception as e:
                logger.debug(f'{table_name} 函数: mysql - > OptimizeDatas -> delete_duplicate -> {e}')
        del all_datas

        if not duplicate_id:  # 如果没有重复数据，则跳过该数据表
            return

        try:
            with self.connection.cursor() as cursor:
                placeholders = ', '.join(['%s'] * len(duplicate_id))
                # 移除冗余数据
                sql = f"DELETE FROM `{table_name}` WHERE id IN ({placeholders})"
                cursor.execute(sql, duplicate_id)
                logger.debug(f"{table_name} -> {date.strftime('%Y-%m-%d')} before: {len(datas)}, remove: {cursor.rowcount}")
            self.connection.commit()  # 提交事务
        except Exception as e:
            logger.error(f'{self.db_name}/{table_name}, {e}')
            self.connection.rollback()  # 异常则回滚

    def delete_duplicate2(self, table_name, except_key=['更新时间']):
        with self.connection.cursor() as cursor:
            sql = f"SELECT * FROM `{table_name}`"  # 如果不包含日期列，则获取全部数据
            cursor.execute(sql)
            datas = cursor.fetchall()
        if not datas:
            return
        duplicate_id = []  # 出现重复的 id
        all_datas = []  # 迭代器
        for data in datas:
            for e_key in except_key:
                if e_key in data.keys():  # 在检查重复数据时，不包含 更新时间 字段
                    del data[e_key]
            delete_id = data['id']
            del data['id']
            data = re.sub(r'\.0+\', ', '\', ', str(data))  # 统一移除小数点后面的 0
            if data in all_datas:  # 数据出现重复时
                duplicate_id.append(delete_id)  # 添加 id 到 duplicate_id
                continue
            all_datas.append(data)  # 数据没有重复
        del all_datas

        if not duplicate_id:  # 如果没有重复数据，则跳过该数据表
            return

        try:
            with self.connection.cursor() as cursor:
                placeholders = ', '.join(['%s'] * len(duplicate_id))
                # 移除冗余数据
                sql = f"DELETE FROM `{table_name}` WHERE id IN ({placeholders})"
                cursor.execute(sql, duplicate_id)
                logger.info(f"{table_name} -> before: {len(datas)}, "
                      f"remove: {cursor.rowcount}")
            self.connection.commit()  # 提交事务
        except Exception as e:
            logger.error(f'{self.db_name}/{table_name}, {e}')
            self.connection.rollback()  # 异常则回滚

    def database_list(self):
        """ 获取所有数据库 """
        connection = self.keep_connect(_db_name=self.db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()  # 获取所有数据库的结果
        connection.close()
        return databases

    def table_list(self, db_name):
        """ 获取指定数据库的所有数据表 """
        connection = self.keep_connect(_db_name=self.db_name, _config=self.config, max_try=10)
        if not connection:
            return
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")  # 检查数据库是否存在
                database_exists = cursor.fetchone()
                if not database_exists:
                    logger.info(f'{db_name}: 数据表不存在!')
                    return
        except Exception as e:
            logger.error(f'002 {e}')
            return
        finally:
            connection.close()  # 断开连接

        self.config.update({'database': db_name})  # 添加更新 config 字段
        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()  # 获取所有数据表
        connection.close()
        return tables

    def table_datas(self, db_name, table_name, date):
        """
        获取指定数据表的数据, 按天获取
        """
        self.config.update({'database': db_name})  # 添加更新 config 字段
        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        try:
            with connection.cursor() as cursor:
                sql = f"SELECT * FROM `{table_name}` WHERE {'日期'} BETWEEN '%s' AND '%s'" % (date, date)
                cursor.execute(sql)
                results = cursor.fetchall()
        except Exception as e:
            logger.error(f'001 {e}')
        finally:
            connection.close()
        return results

    def day_list(self, start_date, end_date):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        date_list = []
        while start_date <= end_date:
            date_list.append(pd.to_datetime(start_date.date()))
            start_date += datetime.timedelta(days=1)
        return date_list

    def rename_column(self):
        """ 批量修改数据库的列名 """
        """
        # for db_name in ['京东数据2', '推广数据2', '市场数据2', '生意参谋2', '生意经2', '属性设置2',]:
        #     s = OptimizeDatas(username=username, password=password, host=host, port=port)
        #     s.db_name = db_name
        #     s.rename_column()
        """
        tables = self.table_list(db_name=self.db_name)
        for table_dict in tables:
            for key, table_name in table_dict.items():
                self.config.update({'database': self.db_name})  # 添加更新 config 字段
                self.connection = self.keep_connect(_db_name=self.db_name, _config=self.config, max_try=10)
                if not self.connection:
                    return
                with self.connection.cursor() as cursor:
                    cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")  # 查询数据表的列信息
                    columns = cursor.fetchall()
                    columns = [{column['Field']: column['Type']} for column in columns]
                    for column in columns:
                        for key, value in column.items():
                            if key.endswith('_'):
                                new_name = re.sub(r'_+$', '', key)
                                sql = f"ALTER TABLE `{table_name}` CHANGE COLUMN {key} {new_name} {value}"
                                cursor.execute(sql)
                self.connection.commit()
        if self.connection:
            self.connection.close()


if __name__ == '__main__':
    pass
