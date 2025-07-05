import hashlib
import json
from collections import OrderedDict
import time
import requests
class wdtapi():
    def __init__(self) -> None:
        self.appkey = "2a2fe68b4cdf80a2b759fb7bd9490f3b"
        self.appName = "zlwl"
        self.sid = "zlwl"

    # 获取登录令牌
    def __getAccessToken__(self, json_body : dict , timestamp : str) -> str:
        params = [
            ("appName", self.appName),
            ("body", json_body),
            ("sid", self.sid),
            ("timestamp", timestamp)
        ]
        # 生成签名字符串
        sign_str = self.appkey
        for key, value in params:
            sign_str += key + value
        sign_str += self.appkey
        # 计算MD5签名
        signature = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        return signature

    # 获取货位库存
    def __getHwkc__(self):
        url = "https://openapi.qizhishangke.com/api/openservices/stockSpec/v1/getOpenApiStockSpecPositionList"
        request_body = {
            "pageNo": 1,
            "pageSize": 1000
            }
        json_body = json.dumps(request_body, separators=(',', ':'))
        timestamp = str(int(time.time()))
        query_params = {
            "sid":self.sid,
            "appName":self.appName,
            "timestamp":timestamp,
            "sign":self.__getAccessToken__(json_body=json_body,timestamp=timestamp)
        }
        headers = {"Content-Type": "application/json"}
        print(url)
        print("query_params:" + str(query_params))
        print("json_body:" + str(json_body))
        response = requests.post(url=url, params=query_params, data=json_body, headers=headers)
        print(response.url)
        print(response.text)
wdtapi().__getHwkc__()