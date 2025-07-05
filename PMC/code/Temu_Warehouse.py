from .FeiShuAPI import feishuapi
from .WdtRPA import wdtrpa
import requests
import json
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os
from urllib.parse import unquote_plus
import pandas as pd

class Wdtwarehouse:

    def __init__(self):
        pass

    def get_bitable_datas(self, app_token, table_id, filter_condition, page_token='', page_size=20) -> json:

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search?page_size={page_size}&page_token={page_token}&user_id_type=user_id"
        payload = json.dumps(filter_condition)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {feishuapi().__getTenantAccessToken__()}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()

    def FEISHU_FBA_DICT(self,app_token, table_id) -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        while has_more:
            filter_condition = {
                "field_names": [],
                "filter": {
                    "conjunction": "and",
                    "conditions": []
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = app_token, table_id = table_id, filter_condition=filter_condition, page_token = page_token, page_size=500)
            if response['code'] == 0:
                feishu_datas.extend(response['data']['items'])
                has_more = response['data']['has_more']
                if has_more == False:
                    break
                page_token = response['data']['page_token']
            else:
                raise Exception(response['msg'])
        result_list = []
        for feishu_data in feishu_datas:
            result_list.append(feishu_data["record_id"])
        return result_list
    
    def project_Temu_Warehouse(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        # 初始化WebDriver
        driver = webdriver.Chrome(options=options)
        # 打开网页
        driver.get('https://kj.qizhishangke.com/user/login')
        driver.maximize_window()  # 最大化窗口
        # 登录模块 /html/body/div[3]/div/div[2]/div/div/footer/div/button[2]
        # 使用设置的账号和密码填充输入框
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div/main/div[2]/div/form/div[2]/div[1]/div/div/input').send_keys("zlwl")
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div/main/div[2]/div/form/div[2]/div[2]/div/div[1]/input').send_keys("duhonghui")
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div/main/div[2]/div/form/div[2]/div[3]/div/div/input').send_keys("duhonghui@2025")
        # 提交表单
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div/main/div[2]/div/form/div[2]/button').click()
        time.sleep(3)
        driver.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/div/div/footer/div/button[2]').click()
        time.sleep(5)
        for cookie in driver.get_cookies():
            if cookie["name"] == 'Admin-Token':
                token = unquote_plus(cookie['value'])
        WDTResult = wdtrpa(token=token).__getKCdata__()
        driver.close()
        driver.quit()
        # FBA库存明细
        insert_data_list = []
        for _data in WDTResult:
            print(_data)
            try:
                costPrice = float(_data["costPrice"])
            except:
                costPrice = 0
            try:
                totalCost = float(_data["totalCost"])
            except:
                totalCost = 0
            pay_dict = {
                "仓库":_data["warehouseName"],
                "图片URL":_data["imgUrl"],
                "SKU":_data["goodsNo"],
                "品名":_data["goodsName"],
                "单位成本":costPrice,
                "可用库存量":_data["canDeliverNum"],
                "库存总量":_data["stockNum"],
                "库存成本":totalCost
            }
            insert_data_list.append({"fields":pay_dict})
        delete_data_list = self.FEISHU_FBA_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tbl41VMXU1aD6YZk")
        for _data in [delete_data_list[i:i + 500] for i in range(0, len(delete_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbl41VMXU1aD6YZk', payload_dict = payload_dict)
        # 以500为划分，更新回飞书表格，正常的更新
        for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
            payload_dict = {"records":_data}
            print(feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbl41VMXU1aD6YZk', payload_dict = payload_dict))
    def main(self):
        self.project_Temu_Warehouse()
