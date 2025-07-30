# -*- coding:utf-8 -*-
import datetime
import requests
import json
import os
import sys
import re
import time
import warnings
import platform
import getpass
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import pymysql
import pandas as pd
from mdbq.log import spider_logging
from mdbq.mysql import mysql
from mdbq.mysql import s_query
from mdbq.config import config
from mdbq.other import ua_sj
from mdbq.other import otk

dir_path = os.path.expanduser("~")
config_file = os.path.join(dir_path, 'spd.txt')
content = config.read_config(file_path=config_file)
username, password, host, port = content['username'], content['password'], content['host'], content['port']

# m_engine = mysql.MysqlUpload(username=username, password=password, host=host, port=port, charset='utf8mb4')
uld = uploader.MySQLUploader(username=username, password=password, host=host, port=int(port), pool_size=10)
# 实例化一个数据查询类，用来获取 cookies 表数据
download = s_query.QueryDatas(username=username, password=password, host=host, port=port)
logger = mylogger.MyLogger(
    name='aikucun',
    logging_mode='file',
    log_level='info',
    log_file='aikucun.log',
    log_format='json',
    max_log_size=50,
    backup_count=5,
    enable_async=False,  # 是否启用异步日志
    sample_rate=1,  # 采样50%的DEBUG/INFO日志
    sensitive_fields=[],  #  敏感字段列表
    enable_metrics=False,  # 是否启用性能指标
)


def keep_connect(_db_name, _config, max_try: int=10):
    attempts = 1
    while attempts <= max_try:
        try:
            connection = pymysql.connect(**_config)  # 连接数据库
            return connection
        except Exception as e:
            logger.error(f'{_db_name}: 连接失败，正在重试: {host}:{port}  {attempts}/{max_try} {e}')
            attempts += 1
            time.sleep(30)
    logger.error(f'{_db_name}: 连接失败，重试次数超限，当前设定次数: {max_try}')
    return None


class AikuCun:
    def __init__(self):
        self.url = 'https://gray-merc.aikucun.com/index.html'
        self.db_name = 'cookie文件'
        self.table_name = 'main_aikucun'
        self.shop_name = '万里马爱库存'
        self.token = None
        self.today = datetime.date.today()
        self.start_date = (self.today - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        self.end_date = (self.today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        self.error_count = 0

    def logining(self, shop_name='aikucun', headless=False):
        option = webdriver.ChromeOptions()
        if headless:
            option.add_argument("--headless")  # 设置无界面模式
        # 调整chrome启动配置
        option.add_argument("--disable-gpu")
        option.add_argument("--no-sandbox")
        option.add_argument("--disable-dev-shm-usage")
        option.add_experimental_option("excludeSwitches", ["enable-automation"])
        option.add_experimental_option('excludeSwitches', ['enable-logging'])  # 禁止日志输出，减少控制台干扰
        option.add_experimental_option("useAutomationExtension", False)
        option.add_argument('--ignore-ssl-error')  # 忽略ssl错误
        prefs = {
            'profile.default_content_settings.popups': 0,  # 禁止弹出所有窗口
            "browser.download.manager. showAlertOnComplete": False,  # 下载完成后不显示下载完成提示框
            "profile.default_content_setting_values.automatic_downloads": 1,  # 允许自动下载多个文件
        }

        option.add_experimental_option('perfLoggingPrefs', {
            'enableNetwork': True,
            'enablePage': False,
        })
        option.set_capability("goog:loggingPrefs", {
            'browser': 'ALL',
            'performance': 'ALL',
        })
        option.set_capability("goog:perfLoggingPrefs", {
            'enableNetwork': True,
            'enablePage': False,
            'enableTimeline': False
        })

        option.add_experimental_option('prefs', prefs)
        option.add_experimental_option('excludeSwitches', ['enable-automation'])  # 实验性参数, 左上角小字

        # # 修改默认下载文件夹路径
        # option.add_experimental_option("prefs", {"download.default_directory": f'{upload_path}'})

        # # 通过excludeSwitches参数禁用默认的启动路径
        # option.add_experimental_option('excludeSwitches', ['enable-automation'])

        if platform.system() == 'Windows':
            # 设置 chrome 和 chromedriver 启动路径
            chrome_path = os.path.join(f'C:\\Users\\{getpass.getuser()}', 'chrome\\chrome_win64\\chrome.exe')
            chromedriver_path = os.path.join(f'C:\\Users\\{getpass.getuser()}', 'chrome\\chromedriver.exe')
            # os.environ["webdriver.chrome.driver"] = chrome_path
            option.binary_location = chrome_path  # windows 设置此参数有效
            service = Service(chromedriver_path)
            # service = Service(str(pathlib.Path(f'C:\\Users\\{getpass.getuser()}\\chromedriver.exe')))  # 旧路径
        elif platform.system() == 'Darwin':
            chrome_path = '/usr/local/chrome/Google Chrome for Testing.app'
            chromedriver_path = '/usr/local/chrome/chromedriver'
            os.environ["webdriver.chrome.driver"] = chrome_path
            # option.binary_location = chrome_path  # Macos 设置此参数报错
            service = Service(chromedriver_path)
        else:
            chrome_path = '/usr/local/chrome/Google Chrome for Testing.app'
            chromedriver_path = '/usr/local/chrome/chromedriver'
            os.environ["webdriver.chrome.driver"] = chrome_path
            # option.binary_location = chrome_path  # macos 设置此参数报错
            service = Service(chromedriver_path)
        _driver = webdriver.Chrome(options=option, service=service)  # 创建Chrome驱动程序实例
        _driver.maximize_window()  # 窗口最大化 方便后续加载数据

        # 登录
        _driver.get(url='https://gray-merc.aikucun.com/index.html')  # self.url 可能被修改，这里使用固定页面获取 sign
        time.sleep(0.1)
        _driver.maximize_window()  # 窗口最大化 方便后续加载数据
        wait = WebDriverWait(_driver, timeout=15)
        input_box = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//input[@placeholder="请输入用户名"]')))  #
        input_box.send_keys('广东万里马实业股份有限公司')
        input_box = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//input[@placeholder="请输入密码"]')))  #
        input_box.send_keys('wlm123$$$')
        time.sleep(0.1)
        elements = _driver.find_elements(
            By.XPATH, '//button[@class="merchant_login_btn" and contains(text(), "登录")]')
        _driver.execute_script("arguments[0].click();", elements[0])
        for i in range(100):
            try:
                wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//div[@class="user-info nav-user-slider"]')))
                break
            except:
                time.sleep(5)
        local_storage = _driver.execute_script("return window.localStorage;")
        if 'token' in local_storage.keys():
            self.token = {
                '日期': datetime.datetime.today().strftime('%Y-%m-%d'),
                '平台': '爱库存',
                '店铺名称': self.shop_name,
                'token': local_storage['token'],
                '来源位置': 'localstorage',
                '更新时间': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
        time.sleep(5)
        _driver.quit()

    def save_token(self):
        if not self.token:
            print('self.token 不能为空')
            return
        set_typ = {
            '日期': 'DATE',
            '平台': 'varchar(50)',
            '店铺名称': 'varchar(50)',
            'token': 'varchar(255)',
            '来源位置': 'varchar(50)',
            '更新时间': 'timestamp'
        }
        # 更新至数据库记录
        # m_engine.dict_to_mysql(
        #     db_name=self.db_name,
        #     table_name=self.table_name,
        #     dict_data=self.token,
        # )
        uld.upload_data(
            db_name=self.db_name,
            table_name=self.table_name,
            data=self.token,
            set_typ={},
            primary_keys=[],
            check_duplicate=False,
            update_on_duplicate=False,
            duplicate_columns=[],
            allow_null=False,
            partition_by=None,
            partition_date_column='日期',
            auto_create=True,
            indexes=[],
            transaction_mode='row',  # 事务模式
        )

    def get_data_from_bbx(self, start_date=None, end_date=None, item_type='spu', page_num=1, page_size=300):
        """
        这里获取的数据等同于"查询"按钮的数据, 没有"营销后供货额/供货价" 这2个字段, 如果通过下载按钮的报表则有两个字段
        """
        if start_date:
            self.start_date = start_date
        if end_date:
            self.end_date = end_date
        date_list = otk.dates_between(start_date=self.start_date, end_date=self.end_date)

        df = download.data_to_df(
            db_name=self.db_name,
            table_name=self.table_name,
            start_date='2025-03-07',
            end_date='2039-12-31',
            projection={
                '日期': 1,
                '平台': 1,
                '店铺名称': 1,
                'token': 1,
                '更新时间': 1
            },
        )
        if len(df) == 0:
            self.logining()
            self.save_token()
        else:
            # 仅保留最新日期的数据
            idx = df.groupby(['平台', '店铺名称'])['更新时间'].idxmax()
            df = df.loc[idx][['token']]
            if len(df) == 0:
                print(f'从数据库获取的 token 不能为空')
                return
            self.token = df.iloc[0, 0]

        self.url = f'https://treasurebox.aikucun.com/api/web/merchant/treasure/commodity/{item_type}/list'
        headers = {
            'headers': ua_sj.get_ua(),
            'referer': 'https://treasurebox.aikucun.com/dashboard/commodity/ranking/merchant',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://treasurebox.aikucun.com',
            'system': 'merchant',
            'token': self.token,  # 从浏览器本地存储空间获取
        }
        num = 1
        results = []
        for date in date_list:
            if self.error_count > 5:
                print('已退出请求 -> self.error_count > 5')
                break
            req_date = re.sub('-', '', date)
            data = {
                'beginDate': req_date,
                'brandIds': [],
                'cropId': '',
                'cropName': '',
                'ctgryOneIds': [],
                'ctgryThreeIds': [],
                'ctgryTwoIds': [],
                'dimValue': '',
                'endDate': req_date,
                'merchantShopCode': '',
                'orderByName': 'dealGmv',
                'orderType': 'desc',
                'pageNum': page_num,
                'pageSize': page_size
            }

            res = requests.post(
                url=self.url,
                headers=headers,
                # cookies=cookies,
                data=json.dumps(data)
            )
            print(f'正在获取数据({num}/{len(date_list)}): {item_type}榜单  {date}')
            # print(res.json())
            if not res.json().get('success', None):
                print('没有获取到数据, 请求不成功, 如果连续请求失败 > 5, 则需重新获取cookie后继续')
                num += 1
                self.error_count += 1
                time.sleep(1)
                continue
            if not res.json().get('data', {}).get('rows', None):
                print("返回的数据字典异常, ['data']['rows'] 不能为空")
                num += 1
                self.error_count += 1
                time.sleep(1)
                continue
            results += [(date, res.json()['data']['rows'])]
            num += 1
            time.sleep(1)
            if num % 32 == 0:
                print("避免频繁请求, 正在休眠...")
                # time.sleep(60)

        return results

    def insert_datas(self, data_list, db_name, table_name):
        """数据清洗"""
        if not data_list:
            return
        chanel_name = {
            'availableNum': '可售库存数',
            'availableSkuCnt': '在架sku数',
            'brandName': '品牌名',
            'ctgryOneName': '一级类目名称',
            'ctgryThreeName': '三级类目名称',
            'ctgryTwoName': '二级类目名称',
            'dealBuyerCnt': '支付人数_成交',
            'dealBuyerCntRate': '成交率_成交',
            'dealGmv': '成交gmv',
            'dealIdolCnt': '销售爱豆人数',
            'dealProductCnt': '销售量_成交',
            'dealProductCntRate': '售罄率',
            'dealSkuCnt': '成交sku数',
            'dealTwoCnt': '订单数_成交',
            'downSkuCnt': '可售sku数',
            'etlInsertTime': '数据更新时间',
            'forwardConfirmCnt': '转发爱豆人数',
            'forwardConfirmNum': '转发次数',
            'merStyleNo': '商品款号',  # spu 榜单
            'styleNo': '商品货号',  # sku 榜单
            'orderBuyerCnt': '支付人数_交易',
            'orderBuyerCntRate': '成交率_交易',
            'orderGmv': '下单gmv',
            'orderProductCnt': '销售量_交易',
            'orderSkuCnt': '下单sku数',
            'orderTwoCnt': '订单数_交易',
            'pictureUrl': '图片',
            'pvNum': '浏览量',
            'rn': '序号',
            'spuId': 'spuid',
            'spuName': '商品名称',
            'supplyAmount': '供货额',
            'supplyPerAmount': '供货价',
            'uvNum': '访客量',
            'colorName': '颜色',
            'sizeName': '尺码',
            'barCode': '条码',  # sku榜单   款号 + 颜色编码
        }
        # 移除未翻译的列名
        res_col = [item for item in chanel_name.keys() if chanel_name[item] == '']
        for item in res_col:
            del chanel_name[item]

        _results = []
        for item_ in data_list:
            end_date, d_list = item_
            for main_data_dict in d_list:
                dict_data_before = {}
                # 添加数据
                dict_data_before.update({k: v for k, v in main_data_dict.items()})
                # 初始化 dict_data
                dict_data = {
                    '日期': end_date,
                    '平台': '爱库存',
                    '店铺名称': self.shop_name
                }
                for k, v in dict_data_before.items():
                    # 翻译键名
                    [dict_data.update({name_v: v}) for name_k, name_v in chanel_name.items() if k == name_k]
                    # 没有翻译的键值也要保留
                    not_in_rename = [item for item in dict_data_before.keys() if item not in chanel_name.keys()]
                    [dict_data.update({item: dict_data_before[item]}) for item in not_in_rename]
                dict_data.update(
                    {
                        '更新时间': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                )
                new_dict_data = {}
                for k, v in dict_data.items():
                    if v and str(v).lower() != 'none' and str(v) != 'null':
                        new_dict_data.update({k: v})
                    else:
                        new_dict_data.update({k: 0})
                _results.append(new_dict_data)
        set_typ = {
            '可售库存数': 'INT',
            '在架sku数': 'INT',
            '品牌名': 'varchar(50)',
            '一级类目名称': 'varchar(50)',
            '三级类目名称': 'varchar(50)',
            '二级类目名称': 'varchar(50)',
            '支付人数_成交': 'INT',
            '成交率_成交': 'decimal(10,4)',
            '成交gmv': 'decimal(10,2)',
            '销售爱豆人数': 'INT',
            '销售量_成交': 'INT',
            '售罄率': 'decimal(10,4)',
            '成交sku数': 'INT',
            '订单数_成交': 'INT',
            '可售sku数': 'INT',
            '数据更新时间': 'DATETIME',
            '转发爱豆人数': 'INT',
            '转发次数': 'INT',
            '商品款号': 'varchar(50)',
            '支付人数_交易': 'INT',
            '成交率_交易': 'decimal(10,4)',
            '下单gmv': 'decimal(10,2)',
            '销售量_交易': 'INT',
            '下单sku数': 'INT',
            '订单数_交易': 'INT',
            '图片': 'varchar(255)',
            '浏览量': 'INT',
            '序号': 'INT',
            'spuid': 'varchar(50)',
            '商品名称': 'varchar(50)',
            '供货额': 'decimal(10,2)',
            '供货价': 'decimal(10,2)',
            '访客量': 'INT',
            '颜色': 'varchar(50)',
            '尺码': 'varchar(50)',
            '货号': 'varchar(50)',  # 款号 + 颜色编码
        }
        print(f'{self.shop_name} 正在更新数据库 {db_name} -> {table_name}...')
        if 'spu' in table_name:
            drop_dup = ['日期', '平台', '店铺名称', '商品款号', '访客量']
        else:
            drop_dup = ['日期', '平台', '店铺名称', '条码']
        # m_engine.insert_many_dict(
        #     db_name=db_name,
        #     table_name=table_name,
        #     dict_data_list=_results,
        #     icm_update=drop_dup,  # 唯一组合键
        #     # unique_main_key=['人群id'],
        #     set_typ=set_typ,
        #     allow_not_null=False,  # 创建允许插入空值的列
        # )
        uld.upload_data(
            db_name=db_name,
            table_name=table_name,
            data=_results,
            set_typ=set_typ,  # 定义列和数据类型
            primary_keys=[],  # 创建唯一主键
            check_duplicate=True,  # 检查重复数据
            update_on_duplicate=False,  # 遇到重复时更新数据，默认 False 跳过
            duplicate_columns=drop_dup,  # 指定排重的组合键
            allow_null=False,  # 允许插入空值
            partition_by=None,  # 按年/月分表
            partition_date_column='日期',  # 用于分表的日期列名，默认为'日期'
            auto_create=True,  # 表不存在时自动创建, 默认参数不要更改
            indexes=[],  # 指定索引列
            transaction_mode='row',  # 事务模式
        )

    def get_sign(self):
        sign = 'bbcf5b9cf3d3b8ba9c22550dcba8a3ce97be766f'
        current_timestamp_ms = '1741396070777'
        # current_timestamp_ms = int(round(time.time() * 1000))
        self.url = f'https://treasurebox.aikucun.com/api/web/merchant/treasure/commodity/sku/list?time={current_timestamp_ms}&sign={sign}'
        headers = {
            'headers': ua_sj.get_ua(),
            'referer': 'https://treasurebox.aikucun.com/dashboard/commodity/ranking/merchant',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://treasurebox.aikucun.com',
            # 'system': 'merchant',
            # 'token': self.token,  # 从浏览器本地存储空间获取
        }
        data = {
            'beginDate': '20250307',
            'brandIds': [],
            'cropId': '',
            'cropName': '',
            'ctgryOneIds': [],
            'ctgryThreeIds': [],
            'ctgryTwoIds': [],
            'dimValue': '',
            'endDate': '20250307',
            'merchantShopCode': '',
            'orderByName': 'dealGmv',
            'orderType': 'desc',
            'pageNum': 1,
            'pageSize': 10
        }
        res = requests.post(
            url=self.url,
            headers=headers,
            data=json.dumps(data)
        )
        print(res.json())


def main(start_date, end_date=None, item_type=['spu']):
    ak = AikuCun()
    # ak.get_sign()
    for type_ in item_type:
        if type_ not in ['spu', 'sku']:
            print(f'{item_type} 非法参数: {type_}')
            continue
        for i in range(2):
            data_list = ak.get_data_from_bbx(
                start_date=start_date,
                end_date=end_date,
                item_type=type_,
                page_num=1,
                page_size=300
            )
            if not data_list:
                ak.logining()
                ak.save_token()
                ak.error_count = 0  # 重置错误计数器
            else:
                break

        ak.insert_datas(
            data_list=data_list,
            db_name='爱库存2',
            table_name=f'{type_}榜单'
        )



if __name__ == '__main__':
    main(
        start_date='2025-05-13',
        # end_date='2025-04-28',  # 不传则默认到今天
        item_type=[
            # 'spu',
            'sku'
        ]
    )
