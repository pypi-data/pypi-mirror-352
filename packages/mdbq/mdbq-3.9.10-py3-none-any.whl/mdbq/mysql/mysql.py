# -*- coding:utf-8 -*-
import datetime
import re
import time
from functools import wraps
import warnings
import pymysql
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import os
import logging
import logging.handlers
from mdbq.other import otk
from mdbq.log import mylogger
from typing import Union, List, Dict, Optional, Any, Tuple, Set
from dbutils.pooled_db import PooledDB
import json
import psutil
from collections import OrderedDict
import threading
import concurrent.futures
from collections import defaultdict


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
                        table_name = f'{table_name}_{min_year}-{min_month}'
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


class StatementCache(OrderedDict):
    """LRU缓存策略"""
    def __init__(self, maxsize=100):
        super().__init__()
        self.maxsize = maxsize

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            self.popitem(last=False)


class MySQLUploader:
    def __init__(
            self,
            username: str,
            password: str,
            host: str = 'localhost',
            port: int = 3306,
            charset: str = 'utf8mb4',
            collation: str = 'utf8mb4_0900_ai_ci',  # utf8mb4_0900_ai_ci: 该排序规则对大小写不敏感, utf8mb4_0900_as_cs/utf8mb4_bin: 对大小写敏感
            max_retries: int = 10,
            retry_interval: int = 10,
            pool_size: int = 5,
            connect_timeout: int = 10,
            read_timeout: int = 30,
            write_timeout: int = 30,
            ssl: Optional[Dict] = None
    ):
        """
        :param username: 数据库用户名
        :param password: 数据库密码
        :param host: 数据库主机地址，默认为localhost
        :param port: 数据库端口，默认为3306
        :param charset: 字符集，默认为utf8mb4
        :param collation: 排序规则，默认为utf8mb4_0900_ai_ci

        :param max_retries: 最大重试次数，默认为10
        :param retry_interval: 重试间隔(秒)，默认为10
        :param pool_size: 连接池大小，默认为5
        :param connect_timeout: 连接超时(秒)，默认为10
        :param read_timeout: 读取超时(秒)，默认为30
        :param write_timeout: 写入超时(秒)，默认为30
        :param ssl: SSL配置字典，默认为None
        """
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.charset = charset
        self.collation = collation
        self.max_retries = max(max_retries, 1)
        self.retry_interval = max(retry_interval, 1)
        self.pool_size = max(pool_size, 1)
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self.ssl = ssl
        self._prepared_statements = StatementCache(maxsize=100)
        self._max_cached_statements = 100
        self._table_metadata_cache = {}
        self.metadata_cache_ttl = 300  # 5分钟缓存时间

        # 创建连接池
        self.pool = self._create_connection_pool()

    def _create_connection_pool(self) -> PooledDB:
        """创建数据库连接池"""
        if hasattr(self, 'pool') and self.pool is not None and self._check_pool_health():
            return self.pool

        start_time = time.time()
        self.pool = None

        pool_params = {
            'creator': pymysql,
            'host': self.host,
            'port': self.port,
            'user': self.username,
            'password': self.password,
            'charset': self.charset,
            'cursorclass': pymysql.cursors.DictCursor,
            'maxconnections': self.pool_size,
            'ping': 7,
            'connect_timeout': self.connect_timeout,
            'read_timeout': self.read_timeout,
            'write_timeout': self.write_timeout,
            'autocommit': False
        }

        if self.ssl:
            required_keys = {'ca', 'cert', 'key'}
            if not all(k in self.ssl for k in required_keys):
                error_msg = "SSL配置必须包含ca、cert和key"
                logger.error(error_msg)
                raise ValueError(error_msg)
            pool_params['ssl'] = {
                'ca': self.ssl['ca'],
                'cert': self.ssl['cert'],
                'key': self.ssl['key'],
                'check_hostname': self.ssl.get('check_hostname', False)
            }

        try:
            pool = PooledDB(**pool_params)
            elapsed = time.time() - start_time
            logger.info("连接池创建成功", {
                'pool_size': self.pool_size,
                'time_elapsed': elapsed
            })
            return pool
        except Exception as e:
            elapsed = time.time() - start_time
            self.pool = None
            logger.error("连接池创建失败", {
                'error': str(e),
                'time_elapsed': elapsed
            })
            raise ConnectionError(f"连接池创建失败: {str(e)}")

    def _execute_with_retry(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            start_time = time.time()
            operation = func.__name__

            logger.debug(f"开始执行操作: {operation}", {
                'attempt': 1,
                'max_retries': self.max_retries
            })

            for attempt in range(self.max_retries):
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time

                    if attempt > 0:
                        logger.info("操作成功(重试后)", {
                            'operation': operation,
                            'attempts': attempt + 1,
                            'time_elapsed': elapsed
                        })
                    else:
                        logger.debug("操作成功", {
                            'operation': operation,
                            'time_elapsed': elapsed
                        })

                    return result

                except (pymysql.OperationalError, pymysql.err.MySQLError) as e:
                    last_exception = e

                    # 记录详细的MySQL错误信息
                    error_details = {
                        'operation': operation,
                        'error_code': e.args[0] if e.args else None,
                        'error_message': e.args[1] if len(e.args) > 1 else None,
                        'attempt': attempt + 1,
                        'max_retries': self.max_retries
                    }

                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_interval * (attempt + 1)
                        error_details['wait_time'] = wait_time
                        logger.warning(f"数据库操作失败，准备重试 {error_details}", )
                        time.sleep(wait_time)

                        # 尝试重新连接
                        try:
                            self.pool = self._create_connection_pool()
                            logger.info("成功重新建立数据库连接")
                        except Exception as reconnect_error:
                            logger.error("重连失败", {
                                'error': str(reconnect_error)
                            })
                    else:
                        elapsed = time.time() - start_time
                        error_details['time_elapsed'] = elapsed
                        logger.error(f"操作最终失败 {error_details}")

                except pymysql.IntegrityError as e:
                    elapsed = time.time() - start_time
                    logger.error("完整性约束错误", {
                        'operation': operation,
                        'time_elapsed': elapsed,
                        'error_code': e.args[0] if e.args else None,
                        'error_message': e.args[1] if len(e.args) > 1 else None
                    })
                    raise e

                except Exception as e:
                    last_exception = e
                    elapsed = time.time() - start_time
                    logger.error("发生意外错误", {
                        'operation': operation,
                        'time_elapsed': elapsed,
                        'error_type': type(e).__name__,
                        'error_message': str(e),
                        'error_args': e.args if hasattr(e, 'args') else None
                    })
                    break

            raise last_exception if last_exception else Exception("发生未知错误")

        return wrapper

    def _get_connection(self):
        """从连接池获取连接"""
        try:
            conn = self.pool.connection()
            logger.debug("获取数据库连接")
            return conn
        except Exception as e:
            logger.error(f'{e}')
            raise ConnectionError(f"连接数据库失败: {str(e)}")

    def _check_database_exists(self, db_name: str) -> bool:
        """检查数据库是否存在"""
        db_name = self._validate_identifier(db_name)
        sql = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s"

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (db_name,))
                    exists = bool(cursor.fetchone())
                    logger.debug(f"{db_name} 数据库已存在: {exists}")
                    return exists
        except Exception as e:
            logger.error(f"检查数据库是否存在时出错: {str(e)}")
            raise

    def _create_database(self, db_name: str):
        """创建数据库"""
        db_name = self._validate_identifier(db_name)
        sql = f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET {self.charset} COLLATE {self.collation}"

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                conn.commit()
                logger.info(f"{db_name} 数据库已创建")
        except Exception as e:
            logger.error(f"{db_name}: 无法创建数据库 {str(e)}")
            conn.rollback()
            raise

    def _get_partition_table_name(self, table_name: str, date_value: str, partition_by: str) -> str:
        """
        获取分表名称

        :param table_name: 基础表名
        :param date_value: 日期值
        :param partition_by: 分表方式 ('year' 或 'month')
        :return: 分表名称
        :raises ValueError: 如果日期格式无效或分表方式无效
        """
        try:
            # date_obj = datetime.datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
            date_obj = self._validate_datetime(date_value, True)
        except ValueError:
            try:
                # date_obj = datetime.datetime.strptime(date_value, '%Y-%m-%d')
                date_obj = self._validate_datetime(date_value, True)
            except ValueError:
                error_msg = f"无效的日期格式1: {date_value}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        if partition_by == 'year':
            return f"{table_name}_{date_obj.year}"
        elif partition_by == 'month':
            return f"{table_name}_{date_obj.year}_{date_obj.month:02d}"
        else:
            error_msg = "partition_by must be 'year' or 'month'"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _validate_identifier(self, identifier: str) -> str:
        """
        验证并清理数据库标识符(数据库名、表名、列名)
        防止SQL注入和非法字符

        :param identifier: 要验证的标识符
        :return: 清理后的安全标识符
        :raises ValueError: 如果标识符无效
        """
        if not identifier or not isinstance(identifier, str):
            error_msg = f"无效的标识符: {identifier}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 移除非法字符，只保留字母、数字、下划线和美元符号
        cleaned = re.sub(r'[^\w\u4e00-\u9fff$]', '', identifier)
        if not cleaned:
            error_msg = f"无法清理异常标识符: {identifier}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 检查是否为MySQL保留字
        mysql_keywords = {
            'select', 'insert', 'update', 'delete', 'from', 'where', 'and', 'or',
            'not', 'like', 'in', 'is', 'null', 'true', 'false', 'between'
        }
        if cleaned.lower() in mysql_keywords:
            logger.debug(f"存在MySQL保留字: {cleaned}")
            return f"`{cleaned}`"

        return cleaned

    def _check_table_exists(self, db_name: str, table_name: str) -> bool:
        """检查表是否存在"""
        cache_key = f"{db_name}.{table_name}"
        if cache_key in self._table_metadata_cache:
            cached_time, result = self._table_metadata_cache[cache_key]
            if time.time() - cached_time < self.metadata_cache_ttl:
                return result

        db_name = self._validate_identifier(db_name)
        table_name = self._validate_identifier(table_name)
        sql = """
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (db_name, table_name))
                    result = bool(cursor.fetchone())
        except Exception as e:
            logger.error(f"检查数据表是否存在时发生未知错误: {e}", )
            raise

        # 执行查询并缓存结果
        self._table_metadata_cache[cache_key] = (time.time(), result)
        return result

    def _create_table(
            self,
            db_name: str,
            table_name: str,
            set_typ: Dict[str, str],
            primary_keys: Optional[List[str]] = None,
            date_column: Optional[str] = None,
            indexes: Optional[List[str]] = None,
            allow_null: bool = False
    ):
        """
        创建数据表

        :param db_name: 数据库名
        :param table_name: 表名
        :param set_typ: 列名和数据类型字典 {列名: 数据类型}
        :param primary_keys: 主键列列表
        :param date_column: 日期列名，如果存在将设置为索引
        :param indexes: 需要创建索引的列列表
        """
        db_name = self._validate_identifier(db_name)
        table_name = self._validate_identifier(table_name)

        if not set_typ:
            error_msg = "No columns specified for table creation"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 构建列定义SQL
        column_defs = ["`id` INT NOT NULL AUTO_INCREMENT"]

        # 添加其他列定义
        for col_name, col_type in set_typ.items():
            # 跳过id列，因为已经在前面添加了
            if col_name.lower() == 'id':
                continue
            safe_col_name = self._validate_identifier(col_name)
            col_def = f"`{safe_col_name}` {col_type}"

            # 根据allow_null决定是否添加NOT NULL约束
            if not allow_null and not col_type.lower().startswith('json'):
                col_def += " NOT NULL"

            column_defs.append(col_def)

        # 添加主键定义
        if primary_keys:
            # 确保id在主键中
            if 'id' not in [pk.lower() for pk in primary_keys]:
                primary_keys = ['id'] + primary_keys
        else:
            # 如果没有指定主键，则使用id作为主键
            primary_keys = ['id']

        # 添加主键定义
        safe_primary_keys = [self._validate_identifier(pk) for pk in primary_keys]
        primary_key_sql = f", PRIMARY KEY (`{'`,`'.join(safe_primary_keys)}`)"

        # 构建完整SQL
        sql = f"""
        CREATE TABLE IF NOT EXISTS `{db_name}`.`{table_name}` (
            {','.join(column_defs)}
            {primary_key_sql}
        ) ENGINE=InnoDB DEFAULT CHARSET={self.charset} COLLATE={self.collation}
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    logger.info(f"{db_name}.{table_name}: 数据表已创建")

                # 添加普通索引
                index_statements = []

                # 日期列索引
                if date_column and date_column in set_typ:
                    safe_date_col = self._validate_identifier(date_column)
                    index_statements.append(
                        f"ALTER TABLE `{db_name}`.`{table_name}` ADD INDEX `idx_{safe_date_col}` (`{safe_date_col}`)"
                    )

                # 其他索引
                if indexes:
                    for idx_col in indexes:
                        if idx_col in set_typ:
                            safe_idx_col = self._validate_identifier(idx_col)
                            index_statements.append(
                                f"ALTER TABLE `{db_name}`.`{table_name}` ADD INDEX `idx_{safe_idx_col}` (`{safe_idx_col}`)"
                            )

                # 执行所有索引创建语句
                if index_statements:
                    with conn.cursor() as cursor:
                        for stmt in index_statements:
                            cursor.execute(stmt)
                            logger.debug(f"Executed index statement: {stmt}", )

                conn.commit()
                logger.info(f"{db_name}.{table_name}: 索引已添加")

        except Exception as e:
            logger.error(f"{db_name}.{table_name}: 建表失败: {str(e)}")
            conn.rollback()
            raise

    def _validate_datetime(self, value, date_type=False):
        """date_type: 返回字符串类型或者日期类型"""
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d',
            '%Y%m%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y/%-m/%-d',  # 2023/1/8
            '%Y-%m-%-d',  # 2023-01-8
            '%Y-%-m-%-d'  # 2023-1-8
        ]
        for fmt in formats:
            try:
                if date_type:
                    return pd.to_datetime(datetime.datetime.strptime(value, fmt).strftime('%Y-%m-%d'))
                else:
                    return datetime.datetime.strptime(value, fmt).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        raise ValueError(f"无效的日期格式2: {value}")

    def _validate_value(self, value: Any, column_type: str) -> Any:
        """
        验证并清理数据值，根据列类型进行适当转换

        :param value: 要验证的值
        :param column_type: 列的数据类型
        :return: 清理后的值
        :raises ValueError: 如果值转换失败
        """
        if value is None:
            return None

        try:
            column_type_lower = column_type.lower()

            if 'int' in column_type_lower:
                if isinstance(value, (str, bytes)) and not value.strip().isdigit():
                    raise ValueError("非数字字符串无法转换为整数")
                return int(value)
            elif any(t in column_type_lower for t in ['float', 'double', 'decimal']):
                return float(value) if value is not None else None
            elif '日期' in column_type_lower or 'time' in column_type_lower:
                if isinstance(value, (datetime.datetime, pd.Timestamp)):
                    return value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, str):
                    try:
                        return self._validate_datetime(value)  # 使用专门的日期验证方法
                    except ValueError as e:
                        raise ValueError(f"无效日期格式: {value} - {str(e)}")
                return str(value)
            elif 'char' in column_type_lower or 'text' in column_type_lower:
                # 防止SQL注入
                if isinstance(value, str):
                    return value.replace('\\', '\\\\').replace("'", "\\'")
                return str(value)
            elif 'json' in column_type_lower:
                import json
                return json.dumps(value) if value is not None else None
            else:
                return value
        except (ValueError, TypeError) as e:
            error_msg = f"数据类型转换异常 {value} to type {column_type}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _get_table_columns(self, db_name: str, table_name: str) -> Dict[str, str]:
        """获取表的列名和数据类型"""
        db_name = self._validate_identifier(db_name)
        table_name = self._validate_identifier(table_name)
        sql = """
        SELECT COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (db_name, table_name))
                    set_typ = {row['COLUMN_NAME']: row['DATA_TYPE'] for row in cursor.fetchall()}
                    logger.debug(f"{db_name}.{table_name}: 获取表的列信息: {set_typ}")
                    return set_typ
        except Exception as e:
            logger.error(f"无法获取表列信息: {str(e)}")
            raise

    def _upload_to_table(
            self,
            db_name: str,
            table_name: str,
            data: List[Dict],
            set_typ: Dict[str, str],
            primary_keys: Optional[List[str]],
            check_duplicate: bool,
            duplicate_columns: Optional[List[str]],
            allow_null: bool,
            auto_create: bool,
            date_column: Optional[str],
            indexes: Optional[List[str]],
            batch_id: Optional[str] = None
    ):
        """实际执行表上传的方法"""
        # 检查表是否存在
        if not self._check_table_exists(db_name, table_name):
            if auto_create:
                self._create_table(db_name, table_name, set_typ, primary_keys, date_column, indexes,
                                   allow_null=allow_null)
            else:
                error_msg = f"数据表不存在: '{db_name}.{table_name}'"
                logger.error(error_msg)
                raise ValueError(error_msg)

        # 获取表结构并验证
        table_columns = self._get_table_columns(db_name, table_name)
        if not table_columns:
            error_msg = f"获取列失败 '{db_name}.{table_name}'"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 验证数据列与表列匹配
        for col in set_typ:
            if col not in table_columns:
                error_msg = f"列不存在: '{col}' -> '{db_name}.{table_name}'"
                logger.error(error_msg)
                raise ValueError(error_msg)

        # 插入数据
        self._insert_data(
            db_name, table_name, data, set_typ,
            check_duplicate, duplicate_columns
        )

    def _infer_data_type(self, value: Any) -> str:
        """
        根据值推断合适的数据类型

        :param value: 要推断的值
        :return: MySQL数据类型字符串
        """
        if value is None:
            return 'VARCHAR(255)'  # 默认字符串类型

        if isinstance(value, bool):
            return 'TINYINT(1)'
        elif isinstance(value, int):
            # if -128 <= value <= 127:
            #     return 'TINYINT'
            # elif -32768 <= value <= 32767:
            #     return 'SMALLINT'
            # elif -8388608 <= value <= 8388607:
            #     return 'MEDIUMINT'
            if -2147483648 <= value <= 2147483647:
                return 'INT'
            else:
                return 'BIGINT'
        elif isinstance(value, float):
            return 'DECIMAL(10,2)'
        elif isinstance(value, (datetime.datetime, pd.Timestamp)):
            return 'DATETIME'
        elif isinstance(value, datetime.date):
            return 'DATE'
        elif isinstance(value, (list, dict)):
            return 'JSON'
        elif isinstance(value, str):
            # 尝试判断是否是日期时间
            try:
                self._validate_datetime(value)
                return 'DATETIME'
            except ValueError:
                pass

            # 根据字符串长度选择合适类型
            length = len(value)
            if length <= 255:
                return 'VARCHAR(255)'
            elif length <= 65535:
                return 'TEXT'
            elif length <= 16777215:
                return 'MEDIUMTEXT'
            else:
                return 'LONGTEXT'
        else:
            return 'VARCHAR(255)'

    def _prepare_data(
            self,
            data: Union[Dict, List[Dict], pd.DataFrame],
            set_typ: Dict[str, str],
            allow_null: bool = False
    ) -> List[Dict]:
        """
        准备要上传的数据，验证并转换数据类型

        :param data: 输入数据
        :param set_typ: 列名和数据类型字典 {列名: 数据类型}
        :param allow_null: 是否允许空值
        :return: 待上传的数据列表和对应的数据类型
        :raises ValueError: 如果数据验证失败
        """
        # 统一数据格式为字典列表
        if isinstance(data, pd.DataFrame):
            try:
                # 将列名转为小写
                data.columns = [col.lower() for col in data.columns]
                data = data.replace({pd.NA: None}).to_dict('records')
            except Exception as e:
                logger.error(f"数据转字典时发生错误: {e}", )
                raise ValueError(f"数据转字典时发生错误: {e}")
        elif isinstance(data, dict):
            data = [{k.lower(): v for k, v in data.items()}]
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # 将列表中的每个字典键转为小写
            data = [{k.lower(): v for k, v in item.items()} for item in data]
        else:
            error_msg = "数据结构必须是字典、列表、字典列表或dataframe"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 将set_typ的键转为小写
        set_typ = {k.lower(): v for k, v in set_typ.items()}

        # 获取数据中实际存在的列名
        data_columns = set()
        if data:
            data_columns = set(data[0].keys())

        # 过滤set_typ，只保留数据中存在的列
        filtered_set_typ = {}
        for col in data_columns:
            if col in set_typ:
                filtered_set_typ[col] = set_typ[col]
            else:
                # 如果列不在set_typ中，尝试推断类型
                sample_values = [row[col] for row in data if col in row and row[col] is not None][:10]
                if sample_values:
                    inferred_type = self._infer_data_type(sample_values[0])
                    filtered_set_typ[col] = inferred_type
                    logger.debug(f"自动推断列'{col}'的数据类型为: {inferred_type}")
                else:
                    # 没有样本值，使用默认类型
                    filtered_set_typ[col] = 'VARCHAR(255)'
                    logger.debug(f"为列'{col}'使用默认数据类型: VARCHAR(255)")

        prepared_data = []
        for row_idx, row in enumerate(data, 1):
            prepared_row = {}
            for col_name in filtered_set_typ:
                # 跳过id列，不允许外部传入id
                if col_name.lower() == 'id':
                    continue

                if col_name not in row:
                    if not allow_null:
                        error_msg = f"Row {row_idx}: Missing required column '{col_name}' in data"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    prepared_row[col_name] = None
                else:
                    try:
                        prepared_row[col_name] = self._validate_value(row[col_name], filtered_set_typ[col_name])
                    except ValueError as e:
                        error_msg = f"Row {row_idx}, column '{col_name}': {str(e)}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
            prepared_data.append(prepared_row)

        logger.debug(f"已准备 {len(prepared_data)} 行数据")
        return prepared_data, filtered_set_typ

    def upload_data(
            self,
            db_name: str,
            table_name: str,
            data: Union[Dict, List[Dict], pd.DataFrame],
            set_typ: Dict[str, str],
            primary_keys: Optional[List[str]] = None,
            check_duplicate: bool = False,
            duplicate_columns: Optional[List[str]] = None,
            allow_null: bool = False,
            partition_by: Optional[str] = None,
            partition_date_column: str = '日期',
            auto_create: bool = True,
            indexes: Optional[List[str]] = None
    ):
        """
        上传数据到数据库
        """
        upload_start = time.time()
        initial_row_count = len(data) if hasattr(data, '__len__') else 1

        batch_id = f"batch_{int(time.time() * 1000)}"
        success_flag = False

        logger.info("开始上传数据", {
            'batch_id': batch_id,
            'database': db_name,
            'table': table_name,
            'partition_by': partition_by,
            'check_duplicate': check_duplicate,
            'row_count': len(data) if hasattr(data, '__len__') else 1,
            'auto_create': auto_create
        })

        try:
            # 验证参数
            if not set_typ:
                error_msg = "列的数据类型缺失"
                logger.error(error_msg)
                raise ValueError(error_msg)

            if partition_by and partition_by not in ['year', 'month']:
                error_msg = "分表方式必须是 'year' 或 'month'"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # 准备数据
            prepared_data, set_typ = self._prepare_data(data, set_typ, allow_null)

            # 检查数据库是否存在
            if not self._check_database_exists(db_name):
                if auto_create:
                    self._create_database(db_name)
                else:
                    error_msg = f"数据库不存在: '{db_name}'"
                    logger.error(error_msg)
                    raise ValueError(error_msg)

            # 处理分表逻辑
            if partition_by:
                partitioned_data = {}
                for row in prepared_data:
                    try:
                        if partition_date_column not in row:
                            error_msg = f"异常缺失列 '{partition_date_column}'"
                            logger.error(error_msg)
                            continue  # 跳过当前行

                        part_table = self._get_partition_table_name(
                            table_name,
                            str(row[partition_date_column]),
                            partition_by
                        )
                        if part_table not in partitioned_data:
                            partitioned_data[part_table] = []
                        partitioned_data[part_table].append(row)
                    except Exception as e:
                        logger.error("分表处理失败", {
                            'row_data': row,
                            'error': str(e)
                        })
                        continue  # 跳过当前行

                # 对每个分表执行上传
                for part_table, part_data in partitioned_data.items():
                    try:
                        self._upload_to_table(
                            db_name, part_table, part_data, set_typ,
                            primary_keys, check_duplicate, duplicate_columns,
                            allow_null, auto_create, partition_date_column,
                            indexes, batch_id
                        )
                    except Exception as e:
                        logger.error("分表上传失败", {
                            'partition_table': part_table,
                            'error': str(e)
                        })
                        continue  # 跳过当前分表，继续处理其他分表
            else:
                # 不分表，直接上传
                self._upload_to_table(
                    db_name, table_name, prepared_data, set_typ,
                    primary_keys, check_duplicate, duplicate_columns,
                    allow_null, auto_create, partition_date_column,
                    indexes, batch_id
                )

            success_flag = True

        except Exception as e:
            logger.error("上传过程中发生全局错误", {
                'error': str(e),
                'error_type': type(e).__name__
            })
        finally:
            elapsed = time.time() - upload_start
            logger.info("上传处理完成", {
                'batch_id': batch_id,
                'success': success_flag,
                'time_elapsed': elapsed,
                'initial_row_count': initial_row_count
            })

    def _insert_data(
            self,
            db_name: str,
            table_name: str,
            data: List[Dict],
            set_typ: Dict[str, str],
            check_duplicate: bool = False,
            duplicate_columns: Optional[List[str]] = None,
            batch_size: int = 1000,
            batch_id: Optional[str] = None
    ):
        """
        插入数据到表中

        参数:
        db_name: 数据库名
        table_name: 表名
        data: 要插入的数据列表
        set_typ: 列名和数据类型字典 {列名: 数据类型}
        check_duplicate: 是否检查重复
        duplicate_columns: 用于检查重复的列(为空时检查所有列)
        batch_size: 批量插入大小
        batch_id: 批次ID用于日志追踪
        """
        if not data:
            return

        # 获取所有列名（排除id列）
        all_columns = [col for col in set_typ.keys() if col.lower() != 'id']
        safe_columns = [self._validate_identifier(col) for col in all_columns]
        placeholders = ','.join(['%s'] * len(safe_columns))

        # 构建基础SQL语句
        if check_duplicate:
            if not duplicate_columns:
                duplicate_columns = all_columns
            else:
                duplicate_columns = [col for col in duplicate_columns if col != 'id']

            conditions = []
            for col in duplicate_columns:
                col_type = set_typ.get(col, '').lower()

                # 处理DECIMAL类型，使用ROUND确保精度一致
                if col_type.startswith('decimal'):
                    # 提取小数位数，如DECIMAL(10,2)提取2
                    scale_match = re.search(r'decimal\(\d+,(\d+)\)', col_type)
                    scale = int(scale_match.group(1)) if scale_match else 2
                    conditions.append(f"ROUND(`{self._validate_identifier(col)}`, {scale}) = ROUND(%s, {scale})")
                else:
                    conditions.append(f"`{self._validate_identifier(col)}` = %s")

            where_clause = " AND ".join(conditions)

            sql = f"""
                    INSERT INTO `{db_name}`.`{table_name}` 
                    (`{'`,`'.join(safe_columns)}`) 
                    SELECT {placeholders}
                    FROM DUAL
                    WHERE NOT EXISTS (
                        SELECT 1 FROM `{db_name}`.`{table_name}`
                        WHERE {where_clause}
                    )
                    """
        else:
            sql = f"""
                INSERT INTO `{db_name}`.`{table_name}` 
                (`{'`,`'.join(safe_columns)}`) 
                VALUES ({placeholders})
                """

        total_inserted = 0
        total_skipped = 0
        total_failed = 0  # 失败计数器

        # 分批插入数据
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                for i in range(0, len(data), batch_size):
                    batch_start = time.time()
                    batch = data[i:i + batch_size]
                    successful_rows = 0  # 当前批次成功数

                    for row in batch:
                        try:
                            # 准备参数
                            row_values = [row.get(col) for col in all_columns]
                            # 如果是排重检查，添加排重列值
                            if check_duplicate:
                                row_values += [row.get(col) for col in duplicate_columns]

                            cursor.execute(sql, row_values)
                            successful_rows += 1
                            conn.commit()  # 每次成功插入后提交

                        except Exception as e:
                            conn.rollback()  # 回滚当前行的事务
                            total_failed += 1

                            # 记录失败行详细信息
                            error_details = {
                                'batch_id': batch_id,
                                'database': db_name,
                                'table': table_name,
                                'error_type': type(e).__name__,
                                'error_message': str(e),
                                'column_types': set_typ,
                                'duplicate_check': check_duplicate,
                                'duplicate_columns': duplicate_columns
                            }
                            logger.error(f"单行插入失败: {error_details}")
                            continue  # 跳过当前行，继续处理下一行

                    # 更新统计信息
                    if check_duplicate:
                        cursor.execute("SELECT ROW_COUNT()")
                        affected_rows = cursor.rowcount
                        total_inserted += affected_rows
                        total_skipped += len(batch) - affected_rows - (len(batch) - successful_rows)
                    else:
                        total_inserted += successful_rows

                    batch_elapsed = time.time() - batch_start
                    batch_info = {
                        'batch_id': batch_id,
                        'batch_index': i // batch_size + 1,
                        'total_batches': (len(data) + batch_size - 1) // batch_size,
                        'batch_size': len(batch),
                        'successful_rows': successful_rows,
                        'failed_rows': len(batch) - successful_rows,
                        'time_elapsed': batch_elapsed,
                        'rows_per_second': successful_rows / batch_elapsed if batch_elapsed > 0 else 0
                    }
                    logger.debug(f"批次处理完成 {batch_info}")

        logger.info("数据插入完成", {
            'total_rows': len(data),
            'inserted_rows': total_inserted,
            'skipped_rows': total_skipped,
            'failed_rows': total_failed
        })

    def close(self):
        """关闭连接池并记录最终指标"""
        close_start = time.time()

        try:
            if hasattr(self, 'pool') and self.pool is not None:
                # 更安全的关闭方式
                try:
                    self.pool.close()
                except Exception as e:
                    logger.warning("关闭连接池时出错", {
                        'error': str(e)
                    })

                self.pool = None

                elapsed = round(time.time() - close_start, 2)
                logger.info("连接池已关闭", {
                    'close_time_elapsed': elapsed
                })
        except Exception as e:
            elapsed = round(time.time() - close_start, 2)
            logger.error("关闭连接池失败", {
                'error': str(e),
                'close_time_elapsed': elapsed
            })
            raise

    def _check_pool_health(self):
        """定期检查连接池健康状态"""
        try:
            conn = self.pool.connection()
            conn.ping(reconnect=True)
            conn.close()
            return True
        except Exception as e:
            logger.warning("连接池健康检查失败", {
                'error': str(e)
            })
            return False

    def retry_on_failure(max_retries=3, delay=1):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except (pymysql.OperationalError, pymysql.InterfaceError) as e:
                        last_exception = e
                        if attempt < max_retries - 1:
                            time.sleep(delay * (attempt + 1))
                            continue
                        raise MySQLUploaderError(f"操作重试{max_retries}次后失败") from e
                    except Exception as e:
                        raise MySQLUploaderError(f"操作失败: {str(e)}") from e
                raise last_exception if last_exception else MySQLUploaderError("未知错误")

            return wrapper

        return decorator


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
        self.SYSTEM_DATABASES = {
            'information_schema', 'mysql',
            'performance_schema', 'sys'
        }

    def _get_connection(self):
        """从连接池获取连接"""
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
            temp_table = f"temp_{table}_{int(time.time())}"

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
            if hasattr(self, 'pool') and self.pool:
                self.pool.close()
                logger.info("数据库连接池已关闭")
        except Exception as e:
            logger.error(f"关闭连接池时出错: {str(e)}", {'error_type': type(e).__name__})
        finally:
            self.pool = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    uploader = MySQLUploader(
        username='root',
        password='pw',
        host='localhost',
        port=3306,
    )

    # 定义列和数据类型
    set_typ = {
        'name': 'VARCHAR(255)',
        'age': 'INT',
        'salary': 'DECIMAL(10,2)',
        '日期': 'DATE',
        'shop': None,
    }

    # 准备数据
    data = [
        {'日期': '2023-01-8', 'name': 'JACk', 'AGE': '24', 'salary': 555.1545},
        {'日期': '2023-01-15', 'name': 'Alice', 'AGE': 35, 'salary': 100},
        {'日期': '2023-01-15', 'name': 'Alice', 'AGE': 30, 'salary': 0.0},
        {'日期': '2023-02-20', 'name': 'Bob', 'AGE': 25, 'salary': 45000.75}
    ]

    # 上传数据
    uploader.upload_data(
        db_name='测试库',
        table_name='测试表',
        data=data,
        set_typ=set_typ,  # 定义列和数据类型
        primary_keys=[],  # 创建唯一主键
        check_duplicate=False,  # 检查重复数据
        duplicate_columns=[],  # 指定排重的组合键
        allow_null=False,  # 允许插入空值
        partition_by='year',  # 按月分表
        partition_date_column='日期',  # 用于分表的日期列名，默认为'日期'
        auto_create=True,  # 表不存在时自动创建, 默认参数不要更改
        indexes=[],  # 指定索引列
    )

    uploader.close()


def main2():
    deduplicator = MySQLDeduplicator(
        username='root',
        password='pw',
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
    pass
