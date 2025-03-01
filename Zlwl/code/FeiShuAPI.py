import requests
import json

class feishuapi:
    def __init__(self) -> None:
        self.app_id = 'cli_a79cb5f24623900b'
        self.app_secret = 'lvZNTr8MCpoyzNWahuoUhfQUXteKX5X4'

    # 获取登录凭证
    def __getTenantAccessToken__(self) -> str:
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = json.dumps({
            "app_id": self.app_id,
            "app_secret": self.app_secret
        })
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()['tenant_access_token']
    
    # 批量获取记录
    def __getBitableDatas__(self, app_token, table_id, payload_dict) -> json:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_get"
        payload = json.dumps(payload_dict)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.__getTenantAccessToken__()}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()
    
    # 更新多条记录
    def __postUpdatesDatas__(self, app_token, table_id, payload_dict) -> json:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update"
        payload = json.dumps(payload_dict)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.__getTenantAccessToken__()}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()
    
    # 新增多条记录
    def __insertBitableDatas__(self, app_token, table_id, payload_dict):
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
        payload = json.dumps(payload_dict)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.__getTenantAccessToken__()}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()
    
    # 查询记录
    def get_bitable_datas(self, app_token, table_id, page_token='', page_size=20):
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search?page_size={page_size}&page_token={page_token}&user_id_type=user_id"
        payload = json.dumps({})
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.__getTenantAccessToken__()}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()