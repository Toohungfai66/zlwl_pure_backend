import requests

class wdtrpa:

    def __init__(self,token : str) -> None:
        #self.cookies = cookies
        self.token = token
    
    def __getKCdata__(self) -> dict:
        url = "https://erp.qizhishangke.com/a/api/Stock/StockInventorySpec/getStockInventorySpecNew"
        headers = {
            'Token':self.token,
        }
        pageNo = 0
        result_response = []
        while True:
            pageNo += 1
            datas = {
                "searchRule":0,
                "sortField":1,
                "isDesc":1,
                "pageNo":pageNo,
                "pageSize":500
            }
            response = requests.post(url=url,json=datas,headers=headers).json()
            result_response.extend(response["data"]["data"])
            if len(response["data"]["data"]) != 500:
                break
        return result_response