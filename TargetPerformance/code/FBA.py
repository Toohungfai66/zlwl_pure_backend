from .LingXingRPA import lingxingrpa
from .FeiShuAPI import feishuapi
import requests
import json
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from urllib.parse import unquote_plus
class fba:
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

    def FEISHU_FBA_DICT(self):
        page_token = ''
        has_more = True
        feishu_datas = []
        while has_more:
            response = self.get_bitable_datas(app_token = 'MGCzb9OGkaujmysIe8cc6WpwnSd', table_id = 'tbluZil11GgO1ytM', page_token = page_token, page_size = 500)
            if response['code'] == 0:
                feishu_datas.extend(response['data']['items'])
                has_more = response['data']['has_more']
                if has_more == False:
                    break
                page_token = response['data']['page_token']
            else:
                raise Exception(response['msg'])
        result_dict = {}
        fasin_yc_list = []
        for feishu_data in feishu_datas:
            if "父ASIN" in feishu_data["fields"]:
                result_dict.update({feishu_data["fields"]["父ASIN"][0]["text"] + "," +feishu_data["fields"]["仓库"][0]["text"]:feishu_data["record_id"]})
            else:
                continue
        return result_dict

    def main(self):
        cookies = unquote(self.result_cookie)
        LingxingFBAResult = lingxingrpa(cookies=cookies).__getFBAKCdata__()
        FeishuFBAReult = self.FEISHU_FBA_DICT()
        insert_data_list = []
        update_data_list = []
        for _data in LingxingFBAResult:
            fields_dict = {}
            # 获取FBA数据
            try:
                LingxingFBAdata = LingxingFBAResult[_data]
                fields_dict.update({
                    "仓库":LingxingFBAdata["name"],
                    "总库存数量(FBA)":LingxingFBAdata["total"],
                    "总库存金额(FBA)":LingxingFBAdata["total_amount"],
                    "标发在途数量(FBA)":LingxingFBAdata["afn_inbound_shipped_quantity"],
                    "标发在途金额(FBA)":LingxingFBAdata["afn_inbound_shipped_quantity_price"],
                    "实际在途数量(FBA)":LingxingFBAdata["stock_up_num"],
                    "实际在途金额(FBA)":LingxingFBAdata["stock_up_num_price"],
                    "0-60天库龄数量(FBA)":LingxingFBAdata["inv_age_0_to_60_days"],
                    "0-60天库龄金额(FBA)":LingxingFBAdata["inv_age_0_to_60_price"],
                    "61-90天库龄数量(FBA)":LingxingFBAdata["inv_age_61_to_90_days"],
                    "61-90天库龄金额(FBA)":LingxingFBAdata["inv_age_61_to_90_price"],
                    "91-180天库龄数量(FBA)":LingxingFBAdata["inv_age_91_to_180_days"],
                    "91-180天库龄金额(FBA)":LingxingFBAdata["inv_age_91_to_180_price"],
                    "181天及以上库龄数量(FBA)":LingxingFBAdata["inv_age_181_plus_days"],
                    "181天及以上库龄金额(FBA)":LingxingFBAdata["inv_age_181_plus_price"]
                    })
            except:
                fields_dict.update({"数据状态":"待确认"})
            if_data = _data + "," + LingxingFBAResult[_data]["name"]
            if if_data in FeishuFBAReult:
                update_data_list.append({"record_id":FeishuFBAReult[if_data], "fields": fields_dict})
            else:
                fields_dict.update({"父ASIN":_data})
                insert_data_list.append({"fields": fields_dict})

        if len(update_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data}
                # 上传数据
                while True:
                    try:
                        response = feishuapi().__postUpdatesDatas__(app_token = 'MGCzb9OGkaujmysIe8cc6WpwnSd', table_id = 'tbluZil11GgO1ytM', payload_dict = payload_dict)
                        print(response)
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
                        response = feishuapi().__insertBitableDatas__(app_token = 'MGCzb9OGkaujmysIe8cc6WpwnSd', table_id = 'tbluZil11GgO1ytM', payload_dict = payload_dict)
                        print(response)
                        break
                    except:
                        continue
        self.driver.close()
        self.driver.quit()