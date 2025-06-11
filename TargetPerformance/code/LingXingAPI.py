import json
import time
import requests
from .sign import SignBase

class lingxingapi():

    def __init__(self) -> None:
        self.appId = "ak_zmVq5LaPMxZzx"
        self.appSecret = "01FgWJe56AkTEug9FE+W9g=="

    # 获取登录令牌
    def __getAccessToken__(self) -> str:
        url = "https://openapi.lingxing.com/api/auth-server/oauth/access-token"
        payload = {
            "appId":self.appId,
            "appSecret":self.appSecret
        }
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()["data"]["access_token"]
        
    # 查询利润报表-父Asin
    def __StatementProfitParentASIN__(self, startDate : str, endDate : str, searchValue = None, ) -> json:
        result_response = []
        offset = 0
        while True:
            payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "timestamp":int(time.time()),
                "monthlyQuery":"false",
                "startDate":startDate,
                "endDate":endDate,
                "offset": offset,
                "length": 10000,
                "summaryEnabled":"true",
                "currencyCode":"CNY",
            }
            if searchValue != None:
                payload.update({"searchField":"parent_asin", "searchValue":searchValue})
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            headers = {}
            api_url = "/bd/profit/report/open/report/parent/asin/list"
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            try:
                result_response.extend(response["data"]["records"])
            except:
                break
            if len(response["data"]["records"]) != 10000:
                break
            else:
                offset += 10000
            time.sleep(12)
        return result_response
    
    # 查询利润报表-ASIN
    def __StatementProfit__(self, startDate : str, endDate : str, searchValue = None) -> json:
        result_response = []
        offset = 0
        while True:
            payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "timestamp":int(time.time()),
                "monthlyQuery":"false",
                "startDate":startDate,
                "endDate":endDate,
                "offset": offset,
                "length": 10000,
                "summaryEnabled":"true",
                "currencyCode":"CNY",
            }
            if searchValue != None:
                payload.update({"searchField":"asin", "searchValue":searchValue})
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            headers = {}
            print(payload)
            api_url = "/bd/profit/report/open/report/asin/list"
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            print(response)
            result_response.extend(response["data"]["records"])
            if len(response["data"]["records"]) != 10000:
                break
            else:
                offset += 10000
            time.sleep(12)
        return result_response
    # 查询利润报表-SKU
    def __StatementProfitSKU__(self, start_time : str, end_time : str, search_value = None, ) -> json:
        result_response = []
        offset = 0
        while True:
            payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "timestamp":int(time.time()),
                "offset": offset,
                "length": 200,
                "platform_codes":["10008"],
                "store_ids":["110293194527688192", "110293196894021120", "110293197760128000"],
                "currency_code":"0",
                "time_dimension":"1",
                "start_time":start_time,
                "end_time":end_time,
            }
            if search_value != None:
                payload.update({"search_field":2, "search_value":search_value})
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            headers = {}
            api_url = "/basicOpen/multiplatformFinance/profitReportPageList/sku"
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            time.sleep(12)
            result_response.extend(response["data"])
            if len(response["data"]) != 200:
                break
            else:
                offset += 200
        return result_response
    # 查询FBA库存明细
    def __FBAInventoryDetails__(self, offset : int) -> json:
        payload = {
            "app_key":self.appId,
            "access_token":self.__getAccessToken__(),
            "timestamp":int(time.time()),
            "offset": offset,
            "length": 200,
            "search_field":"parent_asin",
            "search_value":"B09ZXLTLQ7"
        }
        payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
        headers = {}
        api_url = "/basicOpen/openapi/storage/fbaWarehouseDetail"
        url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
        response = requests.request("POST", url, headers=headers, json=payload).json()
        return response
    
    # 查询亚马逊店铺列表
    def __AmazonStore__(self) -> json:
        payload = {
            "app_key":self.appId,
            "access_token":self.__getAccessToken__(),
            "timestamp":int(time.time()),
        }
        payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
        headers = {}
        api_url = "/erp/sc/data/seller/lists"
        url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
        response = requests.request("POST", url, headers=headers, json=payload).json()
        return response
     
    # 产品表现
    def __ProductPerformance__(self, start_date : str, end_date : str) -> json:
        result_response = []
        sid = []
        sid_response = self.__AmazonStore__()
        for _data in sid_response["data"]:
            sid.append(_data["sid"])
        for _data in [sid[i:i + 200] for i in range(0, len(sid), 200)]:
            payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "timestamp":int(time.time()),
                "offset": 0,
                "length": 10000,
                "sort_field":"volume",
                "sort_type":"desc",
                "sid":_data,
                "summary_field":"parent_asin",
                "currency_code":"CNY",
                "start_date":start_date,
                "end_date":end_date
            }
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            headers = {}
            api_url = "/bd/productPerformance/openApi/asinList"
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            result_response.extend(response["data"]["list"])
            time.sleep(13)
        return result_response