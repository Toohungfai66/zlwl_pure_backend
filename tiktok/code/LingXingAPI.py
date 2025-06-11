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
    
    # 查询多平台店铺列表
    def __AmazonStore__(self) -> json:
        result_response = []
        offset = 0
        while True:
            payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "timestamp":int(time.time()),
                "offset":offset,
                "length":200
            }
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            headers = {}
            api_url = "/pb/mp/shop/v2/getSellerList"
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            result_response.extend(response["data"]["list"])
            if len(response["data"]["list"]) != 200:
                break
            else:
                offset += 200
        return result_response
    
    # 获取多平台订单
    def __getOrderManagement__(self, start_time, end_time) -> json:
        result_response = []
        offset = 0
        while True:
            payload = {
                "app_key":self.appId,
                "access_token":self.__getAccessToken__(),
                "timestamp":int(time.time()),
                "offset": offset,
                "length": 500,
                "date_type":"global_purchase_time",
                "start_time":int(start_time),
                "end_time":int(end_time),
                "platform_code":["10011"]
            }
            payload.update({"sign":SignBase.generate_sign(self.appId,payload)})
            headers = {}
            api_url = "/pb/mp/order/v2/list"
            url = f"https://openapi.lingxing.com{api_url}?" + "&".join([key + "=" + str(payload[key]) for key in payload])
            response = requests.request("POST", url, headers=headers, json=payload).json()
            result_response.extend(response["data"]["list"])
            if len(response["data"]["list"]) != 500:
                break
            else:
                offset += 500
        return result_response