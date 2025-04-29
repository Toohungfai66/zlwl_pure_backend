import json
import time
import requests
from .sign import SignBase
from typing import Optional,Callable

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

    # 查询亚马逊店铺列表
    def __AmazonStore__(self) -> json:
        payload = {
            "app_key":self.appId,
            "access_token":self.__getAccessToken__(),
            "timestamp":int(time.time()),
            "is_parant_asin_merge":1
        }
        payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
        headers = {}
        api_url = "/erp/sc/data/seller/lists"
        url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
        response = requests.request("POST", url, headers=headers, json=payload).json()
        return response
    
    # 获取采购计划列表 2:待采购
    def __getPlanPurchase__(self, start_date : str, end_date : str, status : list) -> list:
        result_response = []
        offset = 0
        # sid = []
        # sid_response = self.__AmazonStore__()
        # for _data in sid_response["data"]:
        #     sid.append(_data["sid"])
        while True:
            payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "timestamp":int(time.time()),
                "search_field_time":"creator_time",
                "start_date":start_date,
                "end_date":end_date,
                "offset": offset,
                "length": 500,
                "status": status,
            }
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            headers = {}
            api_url = "/erp/sc/routing/data/local_inventory/getPurchasePlans"
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            result_response.extend(response["data"])
            if len(response["data"]) != 500:
                break
            else:
                offset += 500
        return result_response
    
    # 获取库存明细
    def __getInventoryDetails__(self, sku=None) -> list:
        result_response = []
        offset = 0
        while True:
            payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "timestamp":int(time.time()),
                "offset": offset,
                "length": 800,
            }
            if sku != None:
                payload.update({"sku":sku})
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)}) 
            headers = {}
            api_url = "/erp/sc/routing/data/local_inventory/inventoryDetails"
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            result_response.extend(response["data"])
            if len(response["data"]) != 800:
                break
            else:
                offset += 800
        return result_response
    
    # 获取仓库名称
    def __getWarehouseName__(self) -> dict:
        result_response = {}
        offset = 0
        while True:
            payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "timestamp":int(time.time()),
                "search_field_time":"create_time",
                "offset": offset,
                "length": 1000,
            }
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            headers = {}
            api_url = "/erp/sc/data/local_inventory/warehouse"
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            for _data in response["data"]:
                result_response.update({_data["wid"]:_data["name"]})
            if len(response["data"]) != 1000:
                break
            else:
                offset += 1000
        return result_response
    
    # 获取采购单
    def __getOrderPurchase__(self, start_date : str, end_date : str) -> list:
        result_response = []
        offset = 0
        while True:
            payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "timestamp":int(time.time()),
                "search_field_time":"create_time",
                "start_date":start_date,
                "end_date":end_date,
                "offset": offset,
                "length": 500,
            }
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            headers = {}
            api_url = "/erp/sc/routing/data/local_inventory/purchaseOrderList"
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            result_response.extend(response["data"])
            if len(response["data"]) != 500:
                break
            else:
                offset += 500
        return result_response
    
    # 获取销量统计
    def __getSalesStatistics__(self, startDate : str, endDate : str) -> list:
        result_response = []
        offset = 0
        while True:
            payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "timestamp":int(time.time()),
                "startDate":startDate,
                "endDate":endDate,
                "offset": offset,
                "length": 10000,
            }
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            headers = {}
            api_url = "/bd/profit/statistics/open/msku/list"
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            result_response.extend(response["data"]["records"])
            if len(response["data"]["records"]) != 10000:
                break
            else:
                offset += 10000
        time.sleep(13)
        return result_response
    
    # 获取FBA库存明细
    def __getFBADatabase__(self):
        result_response = []
        offset = 0
        while True:
            payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "timestamp":int(time.time()),
                "offset": offset,
                "length": 200,
                "search_field":"parent_asin",
                "fulfillment_channel_type":"FBA"
            }
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            headers = {}
            api_url = "/basicOpen/openapi/storage/fbaWarehouseDetail"
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            result_response.extend(response["data"])
            if len(response["data"]) != 200:
                break
            else:
                offset += 200
        return result_response
    
    # 获取查询亚马逊Listing
    def __getAmzListing__(self, sid : str):
        result_response = []
        offset = 0
        while True:
            payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "timestamp":int(time.time()),
                "offset": offset,
                "length": 1000,
                "sid":sid
            }
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            headers = {}
            api_url = "/erp/sc/data/mws/listing"
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            result_response.extend(response["data"])
            if len(response["data"]) != 1000:
                break
            else:
                offset += 1000
        return result_response

    # 产品表现
    def __ProductPerformance__(self, start_date : str, end_date : str, search_value=None) -> json:
        result_response = []
        sid = []
        sid_response = self.__AmazonStore__()
        for _data in sid_response["data"]:
            sid.append(_data["sid"])
        for _data in [sid[i:i + 200] for i in range(0, len(sid), 200)]:
            time.sleep(13)
            payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "timestamp":int(time.time()),
                "offset": 0,
                "length": 10000,
                "sort_field":"volume",
                "sort_type":"desc",
                "sid":_data,
                "summary_field":"msku",
                "currency_code":"CNY",
                "start_date":start_date,
                "end_date":end_date,
            }
            if search_value != None:
                payload.update({"search_field":"msku","search_value":search_value})
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            headers = {}
            api_url = "/bd/productPerformance/openApi/asinList"
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            result_response.extend(response["data"]["list"])
        return result_response