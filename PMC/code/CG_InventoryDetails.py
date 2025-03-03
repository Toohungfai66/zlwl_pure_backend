from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta  
import json
import requests

class cg_inventorydetails:

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

    def FEISHU_FBA_DICT(self, app_token,table_id,status) -> list:
        page_token = ''
        has_more = True
        feishu_datas = []
        while has_more:
            filter_condition = {
                "field_names": [
                    "SKU",
                    "仓库"
                ],
                "filter": {
                    "conjunction": "and",
                    "conditions": []
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = app_token, table_id = table_id, filter_condition=filter_condition, page_token = page_token, page_size=500)
            if response['code'] == 0:
                feishu_datas.extend(response['data']["items"])
                has_more = response['data']['has_more']
                if has_more == False:
                    break
                page_token = response['data']['page_token']
            else:
                raise Exception(response['msg'])
        if status == 1:
            result_dict = {}
            for feishu_data in feishu_datas:
                result_dict.update({feishu_data["fields"]["SKU"][0]["text"]:feishu_data["record_id"]})
            return result_dict
        else:
            result_list = []
            for feishu_data in feishu_datas:
                result_list.append(feishu_data["record_id"])
            return result_list

    def main(self):
        # 采购计划领星数据整理
        FeishuReult = self.FEISHU_FBA_DICT(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblMT8KYNHF28z5Z',status = 1)
        FeishuReult_kc_list = self.FEISHU_FBA_DICT(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblVmapeaQodlYI8',status = 2)
        FeishuReult_key_list = list(set(FeishuReult.keys()))

        LX_Result_list = []
        for _data in FeishuReult_key_list:
            LX_Result_list.extend(lingxingapi().__getInventoryDetails__(sku=_data))

        warehouse_name = lingxingapi().__getWarehouseName__()
        insert_data_list = []
        LX_data = []
        for _data in LX_Result_list:
            if _data["wid"] in warehouse_name:
                CK = warehouse_name[_data["wid"]]
            else:
                CK = ""
            fields = {
                    "SKU":_data["sku"],
                    "仓库":CK,
                    "可用量":_data["product_valid_num"],
                    "可用锁定量":_data["product_lock_num"],
                    "待到货":_data["quantity_receive"]
                    }
            insert_data_list.append({
                "fields": fields
                })

        if len(FeishuReult_kc_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [FeishuReult_kc_list[i:i + 500] for i in range(0, len(FeishuReult_kc_list), 500)]:
                payload_dict = {"records":_data}
                feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblVmapeaQodlYI8', payload_dict = payload_dict)
        if len(insert_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
                payload_dict = {"records":_data}
                feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblVmapeaQodlYI8', payload_dict = payload_dict)