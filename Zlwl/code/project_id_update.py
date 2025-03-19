from .FeiShuAPI import feishuapi
import requests,json
class project_id_update_class:

    def __init__(self):
        self.app_token = "Krz3bhiFoaw8Ans8i1YchYcfnDc"
        self.table_id = "tblKshONitaIxTbI"
        self.payload_dict = {}

    def get_bitable_datas(self, app_token, table_id, filter_condition, page_token='', page_size=20) -> json:

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search?page_size={page_size}&page_token={page_token}&user_id_type=user_id"
        payload = json.dumps(filter_condition)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {feishuapi().__getTenantAccessToken__()}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()

    def project_feishu(self):
        page_token = ''
        filter_condition = {
            "field_names": [
                "项目名称"
            ],
            "filter": {
                "conjunction": "and",
                "conditions": []
            },
            "automatic_fields": "false"
        }
        response = self.get_bitable_datas(app_token = "Krz3bhiFoaw8Ans8i1YchYcfnDc", table_id = "tblKshONitaIxTbI", filter_condition=filter_condition, page_token = page_token, page_size=500)
        result_dict_original = {}
        for feishu_data in response['data']['items']:
            try:
                result_dict_original.update({feishu_data["fields"]["项目名称"][0]["text"]:feishu_data["record_id"]})
            except:
                continue
            if feishu_data["fields"]["项目名称"][0]["text"] == "项目ID更新":
                self.payload_dict.update({"records":[{"record_id":feishu_data["record_id"],"fields":{"程序运行状态":"程序运行成功"}}]})
                feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)
        # 定义要保存的 JSON 文件的路径
        file_path = "C:\Project\zlwl_pure_backend\Zlwl\static\project_id.json"
        # 以写入模式打开文件
        with open(file_path, 'w', encoding='utf-8') as json_file:
            # 使用 json.dump() 方法将字典写入文件
            json.dump(result_dict_original, json_file, ensure_ascii=False, indent=4)