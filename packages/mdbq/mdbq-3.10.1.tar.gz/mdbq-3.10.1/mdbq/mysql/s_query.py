# -*- coding:utf-8 -*-
import datetime
import re
import time
import warnings
import pymysql
import numpy as np
import pandas as pd
import os
from decimal import Decimal
import logging

warnings.filterwarnings('ignore')
"""
程序专门用来下载数据库数据, 并返回 df, 不做清洗数据操作;
"""
logger = logging.getLogger(__name__)


class QueryDatas:
    def __init__(self, username: str, password: str, host: str, port: int, charset: str = 'utf8mb4'):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.config = {
            'host': self.host,
            'port': int(self.port),
            'user': self.username,
            'password': self.password,
            'charset': charset,  # utf8mb4 支持存储四字节的UTF-8字符集
            'cursorclass': pymysql.cursors.DictCursor,
        }

    def check_condition(self, db_name, table_name, condition):
        """ 按指定条件查询数据库，并返回 """
        if self.check_infos(db_name, table_name) == False:
            return

        self.config.update({'database': db_name})
        connection = pymysql.connect(**self.config)  # 重新连接数据库
        with connection.cursor() as cursor:
            sql = f"SELECT 更新时间 FROM {table_name} WHERE {condition}"
            # logger.info(sql)
            cursor.execute(sql)
            columns = cursor.fetchall()
            return columns

    def data_to_df(self, db_name, table_name, start_date, end_date, projection: dict = None):
        """
        从数据库表获取数据到DataFrame，支持列筛选和日期范围过滤
        Args:
            db_name: 数据库名
            table_name: 表名
            start_date: 起始日期（包含）
            end_date: 结束日期（包含）
            projection: 列筛选字典，e.g. {'日期': 1, '场景名字': 1}
        """
        # 初始化默认参数
        projection = projection or {}
        df = pd.DataFrame()
        # 日期处理
        start_date = pd.to_datetime(start_date or '1970-01-01').strftime('%Y-%m-%d')
        end_date = pd.to_datetime(end_date or datetime.datetime.today()).strftime('%Y-%m-%d')

        # 前置检查
        if not self.check_infos(db_name, table_name):
            return df

        # 配置数据库连接
        self.config['database'] = db_name
        connection = None

        try:
            connection = pymysql.connect(**self.config)
            with connection.cursor() as cursor:
                # 获取表结构（排除id列）
                cursor.execute(
                    """SELECT COLUMN_NAME 
                    FROM information_schema.columns 
                    WHERE table_schema = %s AND table_name = %s""",
                    (db_name, table_name)
                )
                cols_exist = {col['COLUMN_NAME'] for col in cursor.fetchall()} - {'id'}

                # 处理列选择
                selected_columns = []
                if projection:
                    selected_columns = [k for k, v in projection.items() if v and k in cols_exist]
                    if not selected_columns:
                        logger.info("Warning: Projection 参数不匹配任何数据库字段")
                        return df
                else:
                    selected_columns = list(cols_exist)
                # 构建基础SQL
                quoted_columns = [f'`{col}`' for col in selected_columns]
                base_sql = f"SELECT {', '.join(quoted_columns)} FROM `{db_name}`.`{table_name}`"

                # 添加日期条件
                if '日期' in cols_exist:
                    base_sql += f" WHERE 日期 BETWEEN '{start_date}' AND '{end_date}'"

                # 执行查询
                cursor.execute(base_sql)
                result = cursor.fetchall()

                # 处理结果集
                if result:
                    df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
                    # 类型转换优化
                    decimal_cols = [col for col in df.columns if df[col].apply(lambda x: isinstance(x, Decimal)).any()]
                    df[decimal_cols] = df[decimal_cols].astype(float)

        except Exception as e:
            logger.error(f"Database operation failed: {str(e)}")
        finally:
            if connection:
                connection.close()

        return df

    def columns_to_list(self, db_name, table_name,  columns_name) -> list:
        """
        获取数据表的指定列, 返回列表
        [{'视频bv号': 'BV1Dm4y1S7BU', '下载进度': 1}, {'视频bv号': 'BV1ov411c7US', '下载进度': 1}]
        """
        if self.check_infos(db_name, table_name) == False:  # 检查传入的数据库和数据表是否存在
            return []

        self.config.update({'database': db_name})
        connection = pymysql.connect(**self.config)  # 重新连接数据库
        with connection.cursor() as cursor:
            # 3. 获取数据表的所有列信息
            sql = 'SELECT COLUMN_NAME FROM information_schema.columns WHERE table_schema = %s AND table_name = %s'
            cursor.execute(sql, (db_name, {table_name}))
            columns = cursor.fetchall()
            cols_exist = [col['COLUMN_NAME'] for col in columns]  # 数据表的所有列, 返回 list
            columns_name = [item for item in columns_name if item in cols_exist]
            if len(columns_name) == 0:
                return []
            columns_in = ', '.join(columns_name)
            sql = (f"SELECT {columns_in} FROM {db_name}.{table_name} ")
            cursor.execute(sql)
            column_values = cursor.fetchall()  # 返回指定列，结果是[dict, dict, dict, ...]
            # column_values = [item[column_name] for item in column_values]  # 提取字典的值, 组成列表
        connection.close()
        return column_values

    def dtypes_to_list(self, db_name, table_name) -> list:
        """
        获取数据表的指定列, 返回列表
        [{'视频bv号': 'BV1Dm4y1S7BU', '下载进度': 1}, {'视频bv号': 'BV1ov411c7US', '下载进度': 1}]
        """
        if self.check_infos(db_name, table_name) == False:  # 检查传入的数据库和数据表是否存在
            return []

        self.config.update({'database': db_name})
        connection = pymysql.connect(**self.config)  # 重新连接数据库
        with connection.cursor() as cursor:
            # 3. 获取数据表的所有列信息
            sql = 'SELECT COLUMN_NAME, COLUMN_TYPE FROM information_schema.columns WHERE table_schema = %s AND table_name = %s'
            cursor.execute(sql, (db_name, {table_name}))
            column_name_and_type = cursor.fetchall()
        connection.close()
        return column_name_and_type

    def check_infos(self, db_name, table_name) -> bool:
        """ 检查数据库、数据表是否存在 """
        connection = pymysql.connect(**self.config)  # 连接数据库
        try:
            with connection.cursor() as cursor:
                # 1. 检查数据库是否存在
                cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")  # 检查数据库是否存在
                database_exists = cursor.fetchone()
                if not database_exists:
                    logger.info(f"Database <{db_name}>: 数据库不存在")
                    return False
        finally:
            connection.close()  # 这里要断开连接

        self.config.update({'database': db_name})  # 添加更新 config 字段
        connection = pymysql.connect(**self.config)  # 重新连接数据库
        try:
            with connection.cursor() as cursor:
                # 2. 查询表是否存在
                sql = f"SHOW TABLES LIKE '{table_name}'"
                cursor.execute(sql)
                if not cursor.fetchone():
                    logger.info(f'{db_name} -> <{table_name}>: 表不存在')
                    return False
                return True
        except Exception as e:
            logger.error(e)
            return False
        finally:
            connection.close()  # 断开连接


if __name__ == '__main__':
    conf = ConfigTxt()
    data = conf.config_datas['Windows']['xigua_lx']['mysql']['remoto']
    username, password, host, port = data['username'], data['password'], data['host'], data['port']

    q = QueryDatas(username, password, host, port)
    res = q.columns_to_list(db_name='视频数据', table_name='bilibili视频', columns_name=['视频bv号', '下载进度'])
    logger.info(res)
