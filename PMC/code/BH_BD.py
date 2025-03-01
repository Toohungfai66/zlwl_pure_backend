from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta  
import json
import requests

class bh_bd:

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
                    "FNSKU"
                ],
                "filter": {
                    "conjunction": "and",
                    "conditions": []
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = 'KVZ9bIrm9azOpqseGx3cIkRfn4f', table_id = 'tblrt9FtgUZD6ugh', page_token = page_token, filter_condition=filter_condition, page_size=500)
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
            result_dict.update({feishu_data["fields"]["FNSKU"][0]["text"]:feishu_data["record_id"]})
        return result_dict

    def main(self):
        FeishuReult = self.FEISHU_FBA_DICT()
        result_response = lingxingapi().__getInventoryDetails__()
        AmazonStore_dict = {}
        for _data in lingxingapi().__AmazonStore__()["data"]:
            AmazonStore_dict[_data["sid"]] = _data["name"]
        warehouse_name = lingxingapi().__getWarehouseName__()
        update_data_list = []
        insert_data_list = []
        delete_data_list = []
        delete_data_list_1 = []
        for _data in result_response:
            if len(_data["fnsku"]) == 0:
                continue
            try:
                CK = warehouse_name[_data["wid"]]
            except:
                CK = ""
            pay_dict = {
                "FNSKU":_data["fnsku"],
                "仓库":CK,
                "可用量":_data["product_valid_num"] 
            }
            if _data["fnsku"] in FeishuReult:
                pay_dict["数据状态"] = "更新成功"
                update_data_list.append({"fields":pay_dict,"record_id":FeishuReult[_data["fnsku"]],})
            else:
                pay_dict["数据状态"] = "新增成功"
                insert_data_list.append({"fields":pay_dict})
            delete_data_list.append(_data["fnsku"])

        for _data in set(list(FeishuReult.keys())) - set(delete_data_list):
            delete_data_list_1.append(FeishuReult[_data])

        if len(update_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data}
                feishuapi().__insertBitableDatas__(app_token = 'KVZ9bIrm9azOpqseGx3cIkRfn4f', table_id = 'tblrt9FtgUZD6ugh', payload_dict = payload_dict)

        if len(delete_data_list_1) != 0:
            payload_dict = {"records":delete_data_list_1}
            feishuapi().__deleteBitableDatas__(app_token = 'MGCzb9OGkaujmysIe8cc6WpwnSd', table_id = 'tblrt9FtgUZD6ugh', payload_dict = payload_dict)

        if len(insert_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
                payload_dict = {"records":_data}
                feishuapi().__insertBitableDatas__(app_token = 'KVZ9bIrm9azOpqseGx3cIkRfn4f', table_id = 'tblrt9FtgUZD6ugh', payload_dict = payload_dict)