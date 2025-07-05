from .LingXingRPA import lingxingrpa
from .FeiShuAPI import feishuapi
import requests
import json
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from urllib.parse import unquote_plus
from datetime import datetime, timedelta  

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

    def FEISHU_FBA_DICT(self,app_token,table_id) -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        while has_more:
            response = self.get_bitable_datas(app_token = app_token, table_id = table_id, page_token = page_token, page_size=500)
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

    def main(self,project):
        # 获取基础数据
        cookies = unquote(self.result_cookie)
        LingxingListingResult = lingxingrpa(cookies=cookies).__getListing__()
        self.driver.close()
        self.driver.quit()
        name_open_id_dict = {}
        for _data in ["od-027e3daf1d2d45b1cb46cc4ef3bb4f30"]:
            department_response = feishuapi().__getSubDepartmentId__(department_id=_data)
            for _data_1 in department_response["data"]["items"]:
                departmentuser = feishuapi().__getDepartmentalUsers__(payload_dict={"department_id":_data_1["open_department_id"],"page_size":50})
                if "items" not in departmentuser["data"]:
                    continue
                for _data_2 in departmentuser["data"]["items"]:
                    name_open_id_dict[_data_2["name"]] = _data_2["open_id"]
        # 处理数据
        BH_insert_data_list = []
        CW_insert_data_list = []
        for _data in LingxingListingResult:
            realname = ""
            for _data_1 in _data["principal_list"]:
                realname = realname + _data_1["realname"] + ","
            realname = realname[:-1]
            if len(_data["product_brand_text"]) == 0:
                pp = "无品牌"
            else:
                pp = _data["product_brand_text"]
            # 基础信息
            pay_dict = {
                "FNSKU":_data["fnsku"],
                "MSKU":_data["msku"],
                "SKU":_data["local_sku"],
                "品名":_data["local_name"],
                "子ASIN":_data["asin"],
                "父ASIN":_data["parent_asin"],
                "店铺":_data["seller_name"],
                "站点":_data["marketplace"],
                "品牌":pp,
                "制单日期":datetime.now().strftime("%Y-%m-%d"),
                "具体负责人":realname,
            }
            if _data["thirty_volume"] != None:
                pay_dict["销量(30天)"] = int(_data["thirty_volume"])
            fzr = realname.split(",")[0].replace("余琛瑶","余琛瑶Cali").replace("刘捷Leo","刘捷")
            try:
                if fzr in name_open_id_dict:
                    pay_dict["负责人"] = [{"id":name_open_id_dict[fzr]}]
            except:
                pass
            if project == "bh":
                # 其余表信息
                BH_pay_dict = {
                    "商品图片URL":_data["small_image_url"],
                    "标题":_data["item_name"],
                    "分类":_data["category_text"],
                    "FBA可售":_data["afn_fulfillable_quantity"],
                    "FBA调拨":_data["reserved_fc_transfers"], # 仅取待调仓，因为调仓中存在退货或者不可售的(因素较多)
                    "FBA在途":_data["afn_inbound_shipped_quantity"],
                    "FBA计划入库":_data["afn_inbound_working_quantity"],
                    "成交价":float(_data["listing_price"])
                }
                BH_pay_dict.update(pay_dict)
                BH_insert_data_list.append({"fields": BH_pay_dict})
            if project == "cw":
                if _data["status"] == 1 and realname != "非财务数据":
                    CW_pay_dict = {
                        "Listing状态":_data["status_text"],
                        "目前在售价(原币)":float(_data["listing_price"]),
                        "币种":_data["currency_symbol"],
                        "最近一周广告费(金额)":float(_data["seven_spend"])
                    }
                    if _data["total_volume"] != None:
                        CW_pay_dict["销量(7天)"] = int(_data["total_volume"])
                    if _data["fourteen_volume"] != None:
                        CW_pay_dict["销量(14天)"] = int(_data["fourteen_volume"])
                    if _data["fba_fee"] != None:
                        CW_pay_dict["尾程费(原币)"] = float(_data["fba_fee"])
                    if _data["referral_fee"] != None:
                        CW_pay_dict["平台佣金(原币)"] = float(_data["referral_fee"])
                    CW_pay_dict.update(pay_dict)
                    CW_insert_data_list.append({"fields": CW_pay_dict})
                    # https://qxdw48i58l3.feishu.cn/base/XjL9biLNPaja1Tsb0vRcGGSFnLg?table=tbl336biNGE4zRbG&view=vew1NReNhb

        if project == "bh":
            delete_data_list = self.FEISHU_FBA_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tbl4cEZVqzSo83zl")
            for _data in [delete_data_list[i:i + 500] for i in range(0, len(delete_data_list), 500)]:
                payload_dict = {"records":_data}
                feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbl4cEZVqzSo83zl', payload_dict = payload_dict)

            if len(BH_insert_data_list) != 0:
                # 以500为划分，更新回飞书表格，正常的更新
                for _data in [BH_insert_data_list[i:i + 500] for i in range(0, len(BH_insert_data_list), 500)]:
                    payload_dict = {"records":_data}
                    feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbl4cEZVqzSo83zl', payload_dict = payload_dict)

        if project == "cw":
            delete_data_list = self.FEISHU_FBA_DICT(app_token="XjL9biLNPaja1Tsb0vRcGGSFnLg",table_id="tbl336biNGE4zRbG")
            for _data in [delete_data_list[i:i + 500] for i in range(0, len(delete_data_list), 500)]:
                payload_dict = {"records":_data}
                feishuapi().__deleteBitableDatas__(app_token = 'XjL9biLNPaja1Tsb0vRcGGSFnLg', table_id = 'tbl336biNGE4zRbG', payload_dict = payload_dict)

            if len(CW_insert_data_list) != 0:
                # 以500为划分，更新回飞书表格，正常的更新
                for _data in [CW_insert_data_list[i:i + 500] for i in range(0, len(CW_insert_data_list), 500)]:
                    payload_dict = {"records":_data}
                    feishuapi().__insertBitableDatas__(app_token = 'XjL9biLNPaja1Tsb0vRcGGSFnLg', table_id = 'tbl336biNGE4zRbG', payload_dict = payload_dict)
