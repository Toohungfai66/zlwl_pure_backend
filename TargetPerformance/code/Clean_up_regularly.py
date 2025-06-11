from .FeiShuAPI import feishuapi
import json
import requests

class clean_up_regularly:
    def __init__(self) -> None:
        pass

    def get_bitable_datas(self, app_token, table_id, filter_condition, page_token, page_size=20) -> json:

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search?page_size={page_size}&page_token={page_token}&user_id_type=user_id"
        payload = json.dumps(filter_condition)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {feishuapi().__getTenantAccessToken__()}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()

    def main(self):
        feishu_datas = []
        has_more = True
        page_token = ''
        while has_more:
            filter_condition = {
                "field_names": ["SKU"],
                "filter": {
                    "conjunction": "and",
                    "conditions": [
                    {
                        "field_name": "SKU",
                        "operator": "is",
                        "value": [
                            "None"
                        ]
                    },
                    {
                        "field_name": "数据状态",
                        "operator": "isNot",
                        "value": [
                            "链接已删除"
                        ]
                    }
                    ]
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = 'XHPsbDoxhasv4fswQ9hckwLmnbc', table_id = 'tbl5RlIhqMzC8KkC', filter_condition=filter_condition, page_token = page_token, page_size=500)
            if response['code'] == 0:
                has_more = response['data']['has_more']
                if has_more == False:
                    feishu_datas.extend(response['data']['items'])
                    break
                page_token = response['data']['page_token']
                feishu_datas.extend(response['data']['items'])
            else:
                raise Exception(response['msg'])
        yc_data_list = []
        for _data in feishu_datas:
            try:
                yc_data_list.append({"record_id": _data["record_id"], "fields": {
                "数据状态":"链接已删除",
                }})
            except:
                continue
        # 以500为划分，更新回飞书表格，正常的更新
        for _data in [yc_data_list[i:i + 500] for i in range(0, len(yc_data_list), 500)]:
            payload_dict = {"records":_data}
            # 上传数据
            while True:
                try:
                    print(feishuapi().__postUpdatesDatas__(app_token = 'XHPsbDoxhasv4fswQ9hckwLmnbc', table_id = 'tbl5RlIhqMzC8KkC', payload_dict = payload_dict))
                    break
                except:
                    continue