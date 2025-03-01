from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta  
import json
import requests

class bh_productperformance:

    def __init__(self):
        pass

    def get_bitable_datas(self, app_token, table_id, filter_condition, page_token='', page_size=20) -> json:

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search?page_size={page_size}&page_token={page_token}&user_id_type=user_id"
        payload = json.dumps(filter_condition)
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
            filter_condition = {
                "field_names": [
                    "MSKU",
                    "店铺"
                ],
                "filter": {
                    "conjunction": "and",
                    "conditions": []
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = 'KVZ9bIrm9azOpqseGx3cIkRfn4f', table_id = 'tblzV27KDQw1t96z', page_token = page_token, filter_condition=filter_condition, page_size=500)
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
            result_dict.update({feishu_data["fields"]["MSKU"][0]["text"] + "|" + feishu_data["fields"]["店铺"][0]["text"]:feishu_data["record_id"]})
        return result_dict

    def get_last_seven_days(self) -> list:
        dates = []
        today = datetime.today()
        for i in range(8):
            delta = timedelta(days=i)
            date = today - delta
            dates.append(date.strftime("%Y-%m-%d"))
        dates.reverse()
        return dates

    def main(self):
        feishudata = self.FEISHU_FBA_DICT()
        Lingxingproductperformance = {}
        datasproductperformance = lingxingapi().__ProductPerformance__(start_date=self.get_last_seven_days()[0],end_date=self.get_last_seven_days()[-2])
        for _data in datasproductperformance:
            if _data["cate_rank"] == None:
                _data["cate_rank"] = 0
            categories = ""
            if len(_data["categories"]) == 1:
                categories = _data["categories"][0]
            else:
                for _data_1 in _data["categories"]:
                    categories = categories + _data_1 + ","
            brands = ""
            if len(_data["brands"]) == 1:
                brands = _data["brands"][0]
            else:
                for _data_1 in _data["brands"]:
                    brands = brands + _data_1 + ","
            Lingxingproductdict = {
                    _data["price_list"][0]["seller_sku"] + "|" + _data["price_list"][0]["seller_name"]:{
                        "cate_rank":_data["cate_rank"], # 大类排名
                        "spend":float(_data["spend"]), # 广告花费
                        "categories":categories,
                        "brands":brands
                    }
                }
            if _data["price_list"][0]["seller_sku"] + "|" + _data["price_list"][0]["seller_name"] not in Lingxingproductperformance:
                Lingxingproductperformance.update(Lingxingproductdict)
            elif Lingxingproductperformance[_data["price_list"][0]["seller_sku"] + "|" + _data["price_list"][0]["seller_name"]]["cate_rank"] < _data["cate_rank"]:
                Lingxingproductperformance.update(Lingxingproductdict)
            else:
                continue

        payload_original = []
        for _data in feishudata:
            fields_dict = {"record_id": feishudata[_data]}
            if _data in Lingxingproductperformance:
                fields_dict.update({
                    "fields": {
                        "分类":Lingxingproductperformance[_data]["categories"],
                        "品牌":Lingxingproductperformance[_data]["brands"],
                        "当前广告花费(前七天)":Lingxingproductperformance[_data]["spend"],
                        "当前大类排名(前七天)":Lingxingproductperformance[_data]["cate_rank"]
                    }
                    })
            else:
                fields_dict.update({
                    "fields": {
                        "当前广告花费(前七天)":0,
                        "当前大类排名(前七天)":0
                    }
                    })
            payload_original.append(fields_dict)

        # 原表更新
        if len(payload_original) != 0:
            for _data in [payload_original[i:i + 500] for i in range(0, len(payload_original), 500)]:
                payload_dict = {"records":_data}
                feishuapi().__postUpdatesDatas__(app_token = "KVZ9bIrm9azOpqseGx3cIkRfn4f", table_id = "tblzV27KDQw1t96z", payload_dict = payload_dict)