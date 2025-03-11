import requests

class lingxingrpa:

    def __init__(self, cookies : str) -> None:
        self.x_ak_company_id = "901114485580800512"
        self.cookies = cookies
    
    def __getBDKCdata__(self) -> dict:
        url = "https://erp.lingxing.com/api/storage/lists"
        headers = {
            "x-ak-company-id":self.x_ak_company_id,
            'Auth-Token':self.cookies,
        }
        offset = 0
        result_dict = {}
        while True:
            datas = {
                "wid_list":"6512,8356,11459,11458,12136,12098,4508,14119,13301,14125,13296,14121,13297,14127,13294,14120,13293,14123,13300,14126,13292,14124,13295,14128,13298,14122,13299,8349,10040,10834,13086,6927,7111,8350,9485,7757,13609,13610,13611,6925,13095,6928,11214,12066,6511,8353",
                "mid_list":"",
                "sid_list":"",
                "cid_list":"",
                "bid_list":"",
                "principal_list":"",
                "product_type_list":"",
                "product_attribute":"",
                "product_status":"",
                "search_field":"fnsku",
                "search_value":"",
                "is_sku_merge_show":0,
                "is_hide_zero_stock":1,
                "offset":offset,
                "length":200,
                "sort_field":"",
                "sort_type":"",
                "gtag_ids":"",
                "senior_search_list":"[]",
                "permission_uid_list":"",
                "country_code_list":"",
                "req_time_sequence":"/api/storage/lists$$2"
                }
            response = requests.post(url=url,json=datas,headers=headers).json()
            if len(response["data"]["list"]) == 0:
                break
            for data in response["data"]["list"]:
                if str(data["product_name"]).split("&")[0] + "&" + data["wh_name"] in result_dict:
                    result_dict[str(data["product_name"]).split("&")[0] + "&" + data["wh_name"]] = result_dict[str(data["product_name"]).split("&")[0] + "&" + data["wh_name"]] + int(data["total"])-int(data["section1"])
                else:
                    result_dict[str(data["product_name"]).split("&")[0] + "&" + data["wh_name"]] = int(data["total"])-int(data["section1"])
            offset += 200
        return result_dict