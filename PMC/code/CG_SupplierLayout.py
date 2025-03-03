from .FeiShuAPI import feishuapi
import json
import requests

class cg_supplierlayout:

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

    def FEISHU_FBA_DICT(self, app_token,table_id) -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        while has_more:
            filter_condition = {
                "field_names": [
                    "计划编号",
                ],
                "filter": {
                    "conjunction": "and",
                    "conditions": []
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = app_token, table_id = table_id, filter_condition=filter_condition, page_token = page_token, page_size=500)
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
            result_dict.update({feishu_data["fields"]["计划编号"][0]["text"]:feishu_data["record_id"]})
        return result_dict

    def main(self):
        FeishuReult = self.FEISHU_FBA_DICT(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblMT8KYNHF28z5Z')
        FeishuReult_LX = self.FEISHU_FBA_DICT(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblGK2pKaWMnxzkO')
        FeishuReult_HYH = self.FEISHU_FBA_DICT(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblWf3pdueKsG7rx')

        insert_data_list = []
        for _data in FeishuReult:
            if _data not in FeishuReult_LX:
                insert_data_list.append({
                    "fields":{"计划编号":_data,}
                })
            try:
                del FeishuReult_LX[_data]
                del FeishuReult_HYH[_data]
            except:
                continue

        delete_data_list_LX = list(FeishuReult_LX.values())
        delete_data_list_HYH = list(FeishuReult_HYH.values())

        if len(insert_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
                payload_dict = {"records":_data}
                feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblGK2pKaWMnxzkO', payload_dict = payload_dict)
                feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblWf3pdueKsG7rx', payload_dict = payload_dict)
        if len(delete_data_list_LX) != 0:
            payload_dict = {"records":delete_data_list_LX}
            feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblGK2pKaWMnxzkO', payload_dict = payload_dict)
        if len(delete_data_list_HYH) != 0:
            payload_dict = {"records":delete_data_list_HYH}
            feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblWf3pdueKsG7rx', payload_dict = payload_dict)