from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta  
import json
import requests
import time

class bh_salesstatistics:

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
            date_intervals.append((start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))\

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

    def FEISHU_FBA_DICT(self) -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        while has_more:
            filter_condition = {
                "field_names": [
                    "MSKU"
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
            result_dict.update({feishu_data["fields"]["MSKU"][0]["text"]:feishu_data["record_id"]})
        return result_dict


    def main(self):
        new_date_ranges_290 = []
        new_date_ranges_335 = []
        new_date_ranges_365 = []
        for start_date_str, end_date_str in self._30_age_sal():
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

            new_start_date_365 = start_date - timedelta(days=365)
            new_end_date_365 = end_date - timedelta(days=365)

            new_start_date_335 = start_date - timedelta(days=335)
            new_end_date_335 = end_date - timedelta(days=335)

            new_start_date_290 = start_date - timedelta(days=290)
            new_end_date_290 = end_date - timedelta(days=290)

            # 格式化新的日期区间元组并添加到结果列表中
            new_date_ranges_290.append((new_start_date_290.strftime('%Y-%m-%d'), new_end_date_290.strftime('%Y-%m-%d')))
            new_date_ranges_335.append((new_start_date_335.strftime('%Y-%m-%d'), new_end_date_335.strftime('%Y-%m-%d')))
            new_date_ranges_365.append((new_start_date_365.strftime('%Y-%m-%d'), new_end_date_365.strftime('%Y-%m-%d')))
            
        FeishuReult = self.FEISHU_FBA_DICT()
        result_dict = {}
        new_date_ranges_now = self._30_age_sal()
        if_num = 0
        for date_time in [new_date_ranges_now,new_date_ranges_335,new_date_ranges_365,new_date_ranges_290]:
            if_num += 1
            for _data in date_time:
                Lx_response = lingxingapi().__getSalesStatistics__(startDate=_data[0], endDate=_data[1])
                for _data_1 in Lx_response:
                    try:
                        if _data_1["msku"] not in result_dict:
                            result_dict[_data_1["msku"]] = _data_1["totalSalesQuantity"]
                        else:
                            result_dict[_data_1["msku"]] = result_dict[_data_1["msku"]] + _data_1["totalSalesQuantity"]
                    except:
                        continue
            if if_num == 1:
                table_name = "前30天销量(环比动销)"
            elif if_num == 2:
                table_name = "上年同期前30天销量(同比动销)"
            elif if_num == 3:
                table_name = "上年同期后30天销量(同比增长)"
            else:
                table_name = "上年同期75天后30天销量(同比增长)"
            update_data_list = []
            for _data in result_dict:
                fields = {
                    table_name:result_dict[_data]
                }
                if _data in FeishuReult:
                    update_data_list.append({
                        "record_id":FeishuReult[_data],
                        "fields": fields
                    })
            if len(update_data_list) != 0:
                # 以500为划分，更新回飞书表格，正常的更新
                for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                    payload_dict = {"records":_data}
                    feishuapi().__postUpdatesDatas__(app_token = 'KVZ9bIrm9azOpqseGx3cIkRfn4f', table_id = 'tblzV27KDQw1t96z', payload_dict = payload_dict)