import requests
import json
from urllib.parse import unquote
from datetime import datetime, timedelta  
import datetime as dt
from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi

class waller_target_performance:
    def __init__(self) -> None:
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

    def get_dates_since_last_sunday(self,str_date) -> list:  
        dates = []
        dates_1 = []
        for _data in [17,11]:
            # 使用timedelta计算14天前的日期
            previous_date = str_date - timedelta(days=_data)
            # 将结果格式化为字符串输出（格式可按需调整）
            previous_date_str = previous_date.strftime('%Y-%m-%d')
            dates.append(previous_date_str)
        for _data in [10,4]:
            # 使用timedelta计算14天前的日期
            previous_date = str_date - timedelta(days=_data)
            # 将结果格式化为字符串输出（格式可按需调整）
            previous_date_str = previous_date.strftime('%Y-%m-%d')
            dates_1.append(previous_date_str)
        return [dates,dates_1]

    def main(self):
        date_str = datetime.now()
        # 每周一早上7:00更新  获取14天前的日期两周的数据
        Lx_datetime_weeks = self.get_dates_since_last_sunday(str_date = date_str)
        for date in Lx_datetime_weeks:
            filter_condition = {
                "field_names": [
                    "msku",
                ],
                "filter": {
                    "conjunction": "and",
                    "conditions": [
                    {
                        "field_name": "日期",
                        "operator": "is",
                        "value": [
                            date[0]+"~"+date[-1]
                        ]
                    },
                    {
                        "field_name": "店铺",
                        "operator": "isNot",
                        "value": [
                            "Gintenco溪古"
                        ]
                    }
                    ]
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = 'E3aBbwxUOa5iY3sXnxWccZPknZc', table_id = 'tblU6lxQ6OdF7usl', filter_condition=filter_condition, page_token = '', page_size=1)
            if len(response['data']['items']) != 0:
                continue
            # 获取利润报表数据
            datasstatementprofit = lingxingapi().__StatementProfitSKU__(start_time=date[0], end_time=date[1])
            LingxingProfitResult = {}
            for _data in datasstatementprofit:
                if type(_data["msku_list"]) == list:
                    msku_list = ""
                    for _data_1 in _data["msku_list"]:
                        msku_list = msku_list + _data_1  + ","
                    msku_list = msku_list[:-1]
                else:
                    msku_list = _data["msku_list"]
                LingxingProfitResult.update({
                    msku_list:{
                        "sku":_data["local_name_list"][0]["sku"], # sku
                        "product_name":_data["local_name_list"][0]["product_name"],# 品名
                        "sales_num":int(_data["sales_num"]), # 销量
                        "sales_amount":float(_data["sales_amount"]), # 销售额
                        "gross_profit":float(_data["gross_profit"]), # 毛利润
                        "purchase_cost":float(_data["purchase_cost"]), # 采购成本
                        "firstlet_cost":float(_data["firstlet_cost"]), # 头程成本
                        "SR":float(_data["sales_amount"]) + float(_data["buyer_freight"]) + float(_data["other_income"]) + float(_data["income_return"]) + float(_data["cost_refund"]),# 收入小计
                        "PT":float(_data["platform_fee"]) + float(_data["discount_fee"]) + float(_data["ad_fee"]) + float(_data["adjustment_fee"]) + float(_data["platform_transfer_fee"]) + float(_data["platform_storage_fee"]) + float(_data["platform_other_fee"]),# 平台支出小计
                        "CB":float(_data["purchase_cost"]) + float(_data["firstlet_cost"]) + float(_data["tail_cost"])# 成本支出小计
                    }
                })
            # 直接添加到新增的API中即可，增加一个日期的拼接与录入
            payload_list = []
            for _data in LingxingProfitResult:
                payload_list.append({
                    "fields":{
                        "平台":"Walmart",
                        "日期":date[0]+"~"+date[-1],
                        "msku":_data,
                        "sku":LingxingProfitResult[_data]["sku"],
                        "品名":LingxingProfitResult[_data]["product_name"],
                        "销量实际达成":LingxingProfitResult[_data]["sales_num"],
                        "销售额实际达成":LingxingProfitResult[_data]["sales_amount"],
                        "收入小计实际达成":LingxingProfitResult[_data]["SR"],
                        "平台支出小计实际达成":LingxingProfitResult[_data]["PT"],
                        "采购成本实际达成":LingxingProfitResult[_data]["purchase_cost"],
                        "头程成本实际达成":LingxingProfitResult[_data]["firstlet_cost"],
                        "成本支出小计实际达成":LingxingProfitResult[_data]["CB"],
                        "毛利润实际达成":LingxingProfitResult[_data]["gross_profit"],
                    }
                })
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [payload_list[i:i + 500] for i in range(0, len(payload_list), 500)]:
                payload_dict = {"records":_data}
                # 上传数据
                while True:
                    try:
                        feishuapi().__insertBitableDatas__(app_token="E3aBbwxUOa5iY3sXnxWccZPknZc", table_id="tblU6lxQ6OdF7usl", payload_dict=payload_dict)
                        break
                    except:
                        continue