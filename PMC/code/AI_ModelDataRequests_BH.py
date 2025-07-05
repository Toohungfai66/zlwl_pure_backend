from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta
import pandas as pd
import os

class ai_modeldatarequests_bh:

    def __init__(self):
        pass

    def get_dates_between(self, start_date_str, end_date_str) -> list:
        # 将日期字符串转换为 datetime 对象
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        # 存储日期的列表
        dates = []
        # 当前日期初始化为开始日期
        current_date = start_date

        # 循环生成日期
        while current_date <= end_date:
            # 将当前日期转换为字符串并添加到列表中
            dates.append(current_date.strftime("%Y-%m-%d"))
            # 日期加一天
            current_date += timedelta(days=1)

        return dates

    def get_data(self, start_data:str, end_data:str) -> dict:
        result_dict = {}
        for _date in self.get_dates_between(start_data, end_data):
            datasproductperformance = lingxingapi().__getSalesStatistics__(start_date=_date, end_date=_date)
            Lingxingproductperformance = {}
            for _data in datasproductperformance:
                Lingxingproductdict = {
                        _data["parentAsin"][0] + "," + _data["store_name"][0]:[{
                            '日期': _date, 
                            "销量":_data["volumeTotal"], # 销量
                        }]
                    }#
                Lingxingproductperformance.update(Lingxingproductdict)
            for _data in Lingxingproductperformance:
                if _data not in result_dict:
                    result_dict.update({_data:Lingxingproductperformance[_data]})
                else:
                    result_list = list(result_dict[_data])
                    result_list.append(Lingxingproductperformance[_data][0])
                    result_dict.update({_data:result_list})
        return result_dict

    def is_modified_today(self,filepath):
        # 获取文件修改时间的时间戳
        modify_timestamp = os.path.getmtime(filepath)
        # 转换为datetime对象
        modify_date = datetime.fromtimestamp(modify_timestamp).date()
        # 获取当前日期
        today = datetime.now().date()
        # 比较日期
        return modify_date == today
    
    def get_last_sunday_and_this_saturday(self):
        # 获取今天的日期
        today = datetime.now().date()
        
        # 计算上周日的日期（today.weekday() 返回 0（周一）到 6（周日），0 表示周一，6 表示周日）
        # 上周日的日期 = 今天的日期 - 今天的星期几（转换为 0-6，周日为 6） + 1 天
        last_sunday = today - timedelta(days=today.weekday() + 1)
        
        # 计算本周六的日期（本周六 = 上周日 + 6 天）
        this_saturday = last_sunday + timedelta(days=6)
        
        # 格式化日期为 YYYY-MM-DD 格式
        last_sunday_str = last_sunday.strftime('%Y-%m-%d')
        this_saturday_str = this_saturday.strftime('%Y-%m-%d')
        
        return last_sunday_str, this_saturday_str

    def main(self):
        last_sunday, this_saturday = self.get_last_sunday_and_this_saturday()
        last_sunday = "2025-06-08"
        this_saturday = "2025-06-14"
        # 遍历get_data数据，拼接路径+key+xlsx进行读取，然后录入。读取失败的跳过
        all_data = self.get_data(start_data=last_sunday,end_data=this_saturday)
        for _data in all_data:
            try:
                if self.is_modified_today(f"C:\\Project\\zlwl_pure_backend\\PMC\\static\\ParentAsin_fiels\\{str(_data).replace('/', '-')}.xlsx"):
                    continue
            except:
                continue
            try:
                df = pd.read_excel(f"C:\\Project\\zlwl_pure_backend\\PMC\\static\\ParentAsin_fiels\\{str(_data).replace('/', '-')}.xlsx")
            except:
                continue
            for _data_1 in all_data[_data]:
                new_row = [_data_1["日期"],_data_1["销量"]]
                df.loc[len(df)] = new_row
            df.to_excel(f"C:\\Project\\zlwl_pure_backend\\PMC\static\\ParentAsin_fiels\\{str(_data).replace('/', '-')}.xlsx",index=False)