from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
from .LingXingRPA import lingxingrpa
import json
import requests
from .FeiShuAPI import feishuapi
import requests
import json
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from urllib.parse import unquote_plus

class warehouse:

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

    def FEISHU_FBA_DICT(self,app_token, table_id, project_name) -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        if project_name == "BH":
            field_names = ["FNSKU"]
        elif project_name == "CG":
            field_names = ["品名"]
        else:
            field_names = []
        while has_more:
            filter_condition = {
                "field_names": field_names,
                "filter": {
                    "conjunction": "and",
                    "conditions": []
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = app_token, table_id = table_id, page_token = page_token, filter_condition=filter_condition, page_size=500)
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

    def project_BH(self):
        self.result_response = lingxingapi().__getInventoryDetails__()
        self.AmazonStore_dict = {}
        for _data in lingxingapi().__AmazonStore__()["data"]:
            self.AmazonStore_dict[_data["sid"]] = _data["name"]
        self.warehouse_name = lingxingapi().__getWarehouseName__()
        FeishuReult = self.FEISHU_FBA_DICT(app_token="KVZ9bIrm9azOpqseGx3cIkRfn4f",table_id="tblrt9FtgUZD6ugh",project_name="BH")
        insert_data_list = []
        for _data in self.result_response:
            if len(_data["fnsku"]) == 0:
                continue
            try:
                CK = self.warehouse_name[_data["wid"]]
            except:
                CK = ""
            pay_dict = {
                "FNSKU":_data["fnsku"],
                "仓库":CK,
                "可用量":_data["product_valid_num"] 
            }
            insert_data_list.append({"fields":pay_dict})

        payload_dict = {"records":FeishuReult}
        feishuapi().__deleteBitableDatas__(app_token = 'KVZ9bIrm9azOpqseGx3cIkRfn4f', table_id = 'tblrt9FtgUZD6ugh', payload_dict = payload_dict)
        # 以500为划分，更新回飞书表格，正常的更新
        for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__insertBitableDatas__(app_token = 'KVZ9bIrm9azOpqseGx3cIkRfn4f', table_id = 'tblrt9FtgUZD6ugh', payload_dict = payload_dict)
    # 采购公用仓库存
    def project_CG(self):
        FeishuReult = self.FEISHU_FBA_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tbleZ1v87gYaCB7G",project_name="CG")
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        # 初始化WebDriver
        driver = webdriver.Chrome(options=options)
        # 打开网页
        driver.get('https://erp.lingxing.com/login')
        # 登录模块
        # 使用设置的账号和密码填充输入框
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/form/div[1]/div/div/input').send_keys("xiaodu66")
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/form/div[2]/div/div/input').send_keys("D123456789")
        # 提交表单
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/form/div[4]/div/button').click()
        time.sleep(10)
        for cookie in driver.get_cookies():
            if cookie["name"] == 'authToken':
                result_cookie = unquote_plus(cookie['value'])
        cookies = unquote(result_cookie)
        LingxingBDKCResult = lingxingrpa(cookies=cookies).__getBDKCdata__()
        driver.close()
        driver.quit()
        insert_data_list = []
        for _data in LingxingBDKCResult:
            pay_dict = {
                "品名":str(_data).split("&")[0],
                "仓库名":str(_data).split("&")[1],
                "15天库龄以上(公用量)":LingxingBDKCResult[_data] 
            }
            insert_data_list.append({"fields":pay_dict})
        payload_dict = {"records":FeishuReult}
        feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbleZ1v87gYaCB7G', payload_dict = payload_dict)
        # 以500为划分，更新回飞书表格，正常的更新
        for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbleZ1v87gYaCB7G', payload_dict = payload_dict)
    def main(self):
        self.project_CG()
        # self.project_BH()