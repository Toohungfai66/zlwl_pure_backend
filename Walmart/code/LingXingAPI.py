import json
import time
import requests
from .sign import SignBase
import datetime
from dateutil.relativedelta import relativedelta
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
    
    # 获取销量统计
    def __getSaleStat__(self, start_date : str, end_date : str, data_type : str, result_type : str, date_unit : str) -> list:
        '''
            data_type 1:ASUB 2:父体 3:MSKU 4:SKU 5:SPU 6店铺
            result_type 1:销量 2:订单量 3:销售额  
            date_unit 1:年 2:月 3:周 4:日 
        '''
        result_response = []
        offset = 0
        headers = {
            "Content-Type": "application/json"
            }
        payload = {
            "app_key":self.appId,
            "access_token":self.__getAccessToken__(),
            "timestamp":int(time.time()),
            "result_type":result_type,
            "date_unit":date_unit,
            "start_date":start_date,
            "end_date":end_date,
            "length": 2000,
            "data_type": data_type,
            }
        api_url = "/basicOpen/platformStatisticsV2/saleStat/pageList"
        while True:
            payload.update({"offset": offset,})
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            result_response.extend(response["data"])
            if len(response["data"]) != 2000:
                break
            else:
                offset += 2000
                del payload["sign"]
        return result_response
    
    # 获取在线商品
    def __getOnlineProducts__(self, status : list, store_ids = None) -> list:
        '''
            store_ids 店铺ID
            status  0 PUBLISHED
                    1 READY TO PUBLISH
                    2 IN PROGRESS
                    3 UNPUBLISHED
                    4 STAGE
                    5 SYSTEM PROBLEM
        '''
        result_response = []
        offset = 0
        payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "length":200,
                "status":status
            }
        headers = {}
        api_url = "/basicOpen/multiplatform/walmart/list"
        if store_ids != None:
            payload.update({"store_ids":store_ids})
        while True:
            payload.update({"offset":offset,"timestamp":int(time.time())})
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            result_response.extend(response["data"])
            if len(response["data"]) != 200:
                break
            else:
                offset += 200
                del payload["sign"]
        return result_response