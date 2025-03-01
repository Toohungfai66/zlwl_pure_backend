from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta  
import json
import requests

class bh_procurement:

    def __init__(self):
        pass

    def _30_age_sal(self) -> list:
        # 获取当前日期
        current_date = datetime.now()- timedelta(days=1)
        # current_date = datetime.strptime("2024-12-19", '%Y-%m-%d')
        # 用于存储符合要求的日期区间列表，每个区间用包含起始和结束日期的元组表示
        date_intervals = []

        # 计算完整的7天间隔的区间
        num_full_intervals = (30 // 7)  # 计算前30天里完整的7天间隔的数量
        for i in range(num_full_intervals):
            start_date= current_date - timedelta(days=(i * 7) + 7)  # 正确的结束日期计算，往前推整7天
            end_date= current_date - timedelta(days=(i * 7))
            date_intervals.append((start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

        # 处理剩余不足7天的日期作为单独区间（最开始的区间）
        remaining_days = 30 % 7
        if remaining_days > 0:
            start_date = current_date - timedelta(days=30)
            end_date = current_date - timedelta(days=30 - remaining_days)
            date_intervals.append((start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

        # 正序排列日期区间列表，使其按照时间先后顺序（从最早日期区间到最近日期区间）
        date_intervals = sorted(date_intervals)
        return date_intervals
    def get_bitable_datas(self, app_token, table_id, filter_condition, page_token='', page_size=20) -> json:

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search?page_size={page_size}&page_token={page_token}&user_id_type=user_id"
        payload = json.dumps(filter_condition)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {feishuapi().__getTenantAccessToken__()}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()

    def FEISHU_FBA_DICT(self):
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
            response = self.get_bitable_datas(app_token = 'KVZ9bIrm9azOpqseGx3cIkRfn4f', table_id = 'tblRoQteNoNmylwt', page_token = page_token, filter_condition=filter_condition, page_size=500)
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
        Lx_datetime_weeks = self._30_age_sal()
        result_response = lingxingapi().__getPlanPurchase__(start_date=Lx_datetime_weeks[0][0],end_date=Lx_datetime_weeks[-1][-1],status=[2])
        update_data_list = []
        insert_data_list = []
        delete_data_list = []
        delete_data_list_1 = []
        for _data in result_response:
            if _data["status_text"] != "待采购":
                continue
            if len(_data["fnsku"]) == 0:
                continue
            pay_dict = {
                "FNSKU":_data["fnsku"],
                "仓库":_data["warehouse_name"],
                "采购在途量":_data["quantity_plan"] 
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
                feishuapi().__postUpdatesDatas__(app_token = 'KVZ9bIrm9azOpqseGx3cIkRfn4f', table_id = 'tblRoQteNoNmylwt', payload_dict = payload_dict)

        if len(delete_data_list_1) != 0:
            payload_dict = {"records":delete_data_list_1}
            feishuapi().__deleteBitableDatas__(app_token = 'MGCzb9OGkaujmysIe8cc6WpwnSd', table_id = 'tblRoQteNoNmylwt', payload_dict = payload_dict)

        if len(insert_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
                payload_dict = {"records":_data}
                feishuapi().__insertBitableDatas__(app_token = 'KVZ9bIrm9azOpqseGx3cIkRfn4f', table_id = 'tblRoQteNoNmylwt', payload_dict = payload_dict)