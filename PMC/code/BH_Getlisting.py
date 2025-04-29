from .LingXingRPA import lingxingrpa
from .FeiShuAPI import feishuapi
import requests
import json
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from urllib.parse import unquote_plus
class getlisting:
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
        feishu_datas = []
        while has_more:
            response = self.get_bitable_datas(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbl4cEZVqzSo83zl', page_token = page_token, page_size=500)
            if response['code'] == 0:
                feishu_datas.extend(response['data']['items'])
                has_more = response['data']['has_more']
                if has_more == False:
                    break
                page_token = response['data']['page_token']
            else:
                raise Exception(response['msg'])
        result_dict = {}
        for feishu_data in feishu_datas:
            if "父ASIN" in feishu_data["fields"]:
                result_dict.update({feishu_data["fields"]["FNSKU"][0]["text"] + "|" + feishu_data["fields"]["店铺"][0]["text"]:feishu_data["record_id"]})
            else:
                continue
        return result_dict

    def main(self):
        cookies = unquote(self.result_cookie)
        LingxingListingResult = lingxingrpa(cookies=cookies).__getListing__()
        FeishuListingReult = self.FEISHU_FBA_DICT()
        update_data_list = []
        for _data in LingxingListingResult:
            fields_dict = {}
            if _data not in FeishuListingReult:
                continue
            if LingxingListingResult[_data]["thirty_volume"] == None:
                thirty_volume = 0
            else:
                thirty_volume = int(LingxingListingResult[_data]["thirty_volume"])
            if LingxingListingResult[_data]["yesterday_spend"] == None:
                yesterday_spend = 0
            else:
                yesterday_spend = float(LingxingListingResult[_data]["yesterday_spend"])
            # 获取FBA数据
            try:
                fields_dict["分类"] = LingxingListingResult[_data]["category_text"]
            except:
                fields_dict["分类"] = ""
            try:
                fields_dict["品牌"] = LingxingListingResult[_data]["product_brand_text"]
            except:
                fields_dict["品牌"] = ""
            try:
                fields_dict["前30天销量"] = thirty_volume
            except:
                fields_dict["前30天销量"] = ""
            try:
                fields_dict["昨日广告费"] = yesterday_spend
            except:
                fields_dict["昨日广告费"] = ""
            update_data_list.append({"record_id":FeishuListingReult[_data], "fields": fields_dict})
        if len(update_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data}
                feishuapi().__postUpdatesDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbl4cEZVqzSo83zl', payload_dict = payload_dict)
        self.driver.close()
        self.driver.quit()