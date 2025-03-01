from .LingXingRPA import lingxingrpa
from .FeiShuAPI import feishuapi
import requests
import json
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from urllib.parse import unquote_plus

class wfs:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--log-level=3")
        # 初始化WebDriver
        self.driver = webdriver.Chrome(options=self.options)
        # 打开网页
        self.driver.get('https://erp.lingxing.com/login')
        # 登录模块
        # 使用设置的账号和密码填充输入框
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/form/div[1]/div/div/input').send_keys("xiaodu66")
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/form/div[2]/div/div/input').send_keys("D123456789")
        # 提交表单
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/form/div[4]/div/button').click()
        time.sleep(10)
        for cookie in self.driver.get_cookies():
            if cookie["name"] == 'authToken':
                self.result_cookie = unquote_plus(cookie['value'])
    def get_bitable_datas(self, app_token, table_id, page_token='', page_size=20) -> json:

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search?page_size={page_size}&page_token={page_token}&user_id_type=user_id"
        payload = json.dumps({})
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {feishuapi().__getTenantAccessToken__()}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()

    def FEISHU_FBA_DICT(self) -> dict:
        page_token = ''
        has_more = True
        result_dict = {}
        while has_more:
            response = self.get_bitable_datas(app_token = 'E3aBbwxUOa5iY3sXnxWccZPknZc', table_id = 'tbliuDlYQvywAsgh', page_token = page_token, page_size = 500)
            if response['code'] == 0:
                for _data in response['data']['items']:
                    result_dict[_data['fields']["MSKU"][0]["text"]] = _data["record_id"]
                has_more = response['data']['has_more']
                if has_more == False:
                    break
                page_token = response['data']['page_token']
            else:
                raise Exception(response['msg'])
        return result_dict

    def main(self):
        cookies = unquote(self.result_cookie)
        LingxingFBAResult = lingxingrpa(cookies=cookies).__getWFSKCdata__()
        FeishuFBAReult = self.FEISHU_FBA_DICT()
        insert_data_list = []
        update_data_list = []
        for _data in LingxingFBAResult:
            fields_dict = {}
            # 获取FBA数据
            try:
                LingxingFBAdata = LingxingFBAResult[_data]
                fields_dict.update({
                    "仓库":LingxingFBAdata["warehouseName"],
                    "GTIN码":LingxingFBAdata["gtin"],
                    "平台商品ID":LingxingFBAdata["itemId"],
                    "品名":LingxingFBAdata["productName"],
                    "商品状态":LingxingFBAdata["platformProductStatus"],
                    "总库存数量":LingxingFBAdata["quantity"],
                    "总库存金额":LingxingFBAdata["quantity_cb"],
                    "WFS可售":LingxingFBAdata["availableQuantity"],
                    "无法入库":LingxingFBAdata["unabledWarehousingQuantity"],
                    "标发在途":LingxingFBAdata["inboundQuantity"],
                    "标发在途库存金额":LingxingFBAdata["inboundQuantity_cb"],
                    "近30天入库":LingxingFBAdata["last30DaysUnitsReceived"],
                    "近30天计划入库":LingxingFBAdata["last30DaysPoUnits"]
                    })
            except:
                continue
            if _data in FeishuFBAReult:
                update_data_list.append({"record_id":FeishuFBAReult[_data], "fields": fields_dict})
            else:
                fields_dict.update({"MSKU":_data})
                insert_data_list.append({"fields": fields_dict})

        if len(update_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data}
                # 上传数据
                while True:
                    try:
                        feishuapi().__postUpdatesDatas__(app_token = 'E3aBbwxUOa5iY3sXnxWccZPknZc', table_id = 'tbliuDlYQvywAsgh', payload_dict = payload_dict)
                        break
                    except:
                        continue
        if len(insert_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
                payload_dict = {"records":_data}
                # 上传数据
                while True:
                    try:
                        feishuapi().__insertBitableDatas__(app_token = 'E3aBbwxUOa5iY3sXnxWccZPknZc', table_id = 'tbliuDlYQvywAsgh', payload_dict = payload_dict)
                        break
                    except:
                        continue