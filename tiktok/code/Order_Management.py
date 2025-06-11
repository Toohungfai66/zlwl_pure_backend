from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
import json
import requests
import numpy as np
from datetime import datetime, timedelta
import time

class order_management:
    def __init__(self):
        pass
    def get_last_week_timestamps(self):
        """
        获取上周一 00:00:00 到上周日 23:59:59 的时间戳
        """
        # 获取今天的日期
        today = datetime.now().date()
        
        # 计算今天是星期几（0=星期一，6=星期日）
        weekday = today.weekday()
        
        # 计算上周日的日期（今天往前推 weekday+1 天）
        last_sunday = today - timedelta(days=weekday+1)
        
        # 计算上周一的日期（上周日往前推 6 天）
        last_monday = last_sunday - timedelta(days=6)
        
        # 构造上周日结束时间（23:59:59）
        last_sunday_end = datetime.combine(last_sunday, datetime.max.time())
        
        # 构造上周一开始时间（00:00:00）
        last_monday_start = datetime.combine(last_monday, datetime.min.time())
        
        # 转换为时间戳（秒）
        monday_timestamp = int(last_monday_start.timestamp())
        sunday_timestamp = int(last_sunday_end.timestamp())
        
        return {
            'start': monday_timestamp,  # 上周一 00:00:00 的时间戳
            'end': sunday_timestamp     # 上周日 23:59:59 的时间戳
        }

    def timestamp_to_datetime(self, timestamp):
        """
        将时间戳转换为指定格式的日期字符串
        
        参数:
            timestamp: 时间戳（秒或毫秒）
        
        返回:
            str: 格式化后的日期字符串，格式为 YYYY-MM-DD HH:MM:SS
        """
        # 判断是否为毫秒级时间戳（13位）
        if len(str(int(timestamp))) > 10:
            timestamp = timestamp / 1000.0
        
        # 转换为datetime对象
        dt_object = datetime.fromtimestamp(timestamp)
        
        # 格式化为字符串
        return dt_object.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_week_number(self, date_str):
        """
        计算日期属于当年的第几周，周一到周日为一周
        
        参数:
            date_str: 日期字符串，格式为 YYYY-MM-DD HH:MM:SS
        
        返回:
            int: 当年的周数
        """
        # 将日期字符串转换为datetime对象
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        
        # 获取当年第一天
        first_day_of_year = datetime(dt.year, 1, 1)
        
        # 计算当年第一天是星期几（0=星期一，6=星期日）
        weekday_of_first_day = first_day_of_year.weekday()
        
        # 计算第一周的开始日期（可能是上一年）
        first_week_start = first_day_of_year - timedelta(days=weekday_of_first_day)
        
        # 计算目标日期与第一周开始日期之间的天数差
        days_diff = (dt - first_week_start).days
        
        # 计算周数（整数除法）
        week_number = days_diff // 7 + 1
        
        return week_number
    def main(self):
        sid_response = lingxingapi().__AmazonStore__()
        sid_name_dict = {}
        for _data in sid_response:
            sid_name_dict[_data["store_id"]] = _data["store_name"]
        date_dict = self.get_last_week_timestamps()
        lingxingresult = lingxingapi().__getOrderManagement__(start_time = date_dict["start"], end_time= date_dict["end"])
        status_list = ["无","同步中","已同步","未付款","待审核","待发货","已发货","已取消/不发货","不显示","平台发货"]
        insert_data_list = []
        for _data in lingxingresult:
            fields = {}
            fields["订购时间"] = self.timestamp_to_datetime(timestamp=_data["global_purchase_time"])
            fields["周次"] = self.get_week_number(date_str=fields["订购时间"])
            try:
                fields["店铺"] = sid_name_dict[_data["store_id"]]
            except:
                fields["店铺"] = "无"
            try:
                fields["订单状态"] = status_list[_data["status"]]
            except:
                fields["订单状态"] = status_list[0]
            for _data_1 in _data["item_info"]:
                fields["平台单号"] = _data_1["platform_order_no"]
                fields["MSKU"] = _data_1["msku"]
                fields["物流运费"] = float(_data_1["wms_shipping_price_amount"])
                fields["出库成本"] = float(_data_1["wms_outbound_cost_amount"])
                print(fields)
                insert_data_list.append({"fields":fields})
        if len(insert_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
                payload_dict = {"records":_data}
                print(feishuapi().__insertBitableDatas__(app_token = "Yhu6byt2Wa1lDIss5g5cn0dSnFg", table_id = 'tbldAEhbb1sVVYBb', payload_dict = payload_dict))