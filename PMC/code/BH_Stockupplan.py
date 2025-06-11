from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta  
import json
import requests

class bh_stockupplan:

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
            response = self.get_bitable_datas(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbl4cEZVqzSo83zl', page_token = page_token, filter_condition=filter_condition, page_size=500)
            if response['code'] == 0:
                feishu_datas.extend(response['data']['items'])
                has_more = response['data']['has_more']
                if has_more == False:
                    break
                page_token = response['data']['page_token']
            else:
                raise Exception(response['msg'])
        result_list = []
        for feishu_data in feishu_datas:
            result_list.append(feishu_data["record_id"])
        return result_list

    def main(self):
        name_open_id_dict = {}
        for _data in ["od-027e3daf1d2d45b1cb46cc4ef3bb4f30"]:
            department_response = feishuapi().__getSubDepartmentId__(department_id=_data)
            for _data_1 in department_response["data"]["items"]:
                departmentuser = feishuapi().__getDepartmentalUsers__(payload_dict={"department_id":_data_1["open_department_id"],"page_size":50})
                if "items" not in departmentuser["data"]:
                    continue
                for _data_2 in departmentuser["data"]["items"]:
                    name_open_id_dict[_data_2["name"]] = _data_2["open_id"]
        sid_response = lingxingapi().__AmazonStore__()
        sid = ""
        sid_name_dict = {}
        for _data in sid_response["data"]:
            sid = sid + str(_data["sid"]) + ","
            sid_name_dict[_data["sid"]] = _data["name"]
        sid = sid[:-1]
        result_response = lingxingapi().__getAmzListing__(sid=sid)
        insert_data_list = []
        for _data in result_response:
            if len(_data["fnsku"]) == 0:
                continue
            if _data["is_delete"] == 0:
                if len(_data["principal_info"]) == 0:
                    principal_name = ""
                else:
                    print(_data["principal_info"])
                    principal_name = _data["principal_info"][0]["principal_name"]
                    print(principal_name)
                if principal_name == "余琛瑶":
                    principal_name = "余琛瑶Cali"
                elif principal_name == "刘捷Leo":
                    principal_name = "刘捷"
                pay_dict = {
                    "FNSKU":_data["fnsku"],
                    "商品图片URL":_data["small_image_url"],
                    "MSKU":_data["seller_sku"],
                    "SKU":_data["local_sku"],
                    "品名":_data["local_name"],
                    "标题":_data["item_name"],
                    "子ASIN":_data["asin"],
                    "父ASIN":_data["parent_asin"],
                    "店铺":sid_name_dict[_data["sid"]],
                    "站点":_data["marketplace"],
                    "负责人":principal_name,
                    "制单日期":datetime.now().strftime("%Y-%m-%d"),
                    "FBA可售":_data["afn_fulfillable_quantity"],
                    "FBA调拨":_data["reserved_fc_transfers"],
                    "FBA在途":_data["afn_inbound_shipped_quantity"]
                }
                if principal_name in name_open_id_dict:
                    pay_dict["负责人(人员)"] = [{"id":name_open_id_dict[principal_name]}]
                insert_data_list.append({"fields":pay_dict})
                
        delete_data_list = self.FEISHU_FBA_DICT()
        for _data in [delete_data_list[i:i + 500] for i in range(0, len(delete_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbl4cEZVqzSo83zl', payload_dict = payload_dict)
        if len(insert_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
                payload_dict = {"records":_data}
                print(feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbl4cEZVqzSo83zl', payload_dict = payload_dict))