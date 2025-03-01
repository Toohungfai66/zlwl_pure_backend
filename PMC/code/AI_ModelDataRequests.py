from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta
import pandas as pd

class ai_modeldatarequests:

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
            datasproductperformance = lingxingapi().__ProductPerformance__(start_date=_date, end_date=_date)
            Lingxingproductperformance = {}
            for _data in datasproductperformance:
                if _data["cate_rank"] == None:
                    _data["cate_rank"] = 0
                Lingxingproductdict = {
                        _data["price_list"][0]["seller_sku"] + "_" + _data["parent_asins"][0]["parent_asin"] + "_" + _data["asins"][0]["asin"]:[{
                            '日期': _date, 
                            "销量":_data["volume"], # 销量
                            "广告花费":_data["spend"], # 广告花费
                            "大类排名":_data["cate_rank"], # 大类排名
                        }]
                    }
                if _data["price_list"][0]["seller_sku"] + "_" + _data["parent_asins"][0]["parent_asin"] + "_" + _data["asins"][0]["asin"] not in Lingxingproductperformance:
                    Lingxingproductperformance.update(Lingxingproductdict)
                elif Lingxingproductperformance[_data["price_list"][0]["seller_sku"] + "_" + _data["parent_asins"][0]["parent_asin"] + "_" + _data["asins"][0]["asin"]][0]["大类排名"] < _data["cate_rank"]:
                    Lingxingproductperformance.update(Lingxingproductdict)
                else:
                    continue
            for _data in Lingxingproductperformance:
                if _data not in result_dict:
                    result_dict.update({_data:Lingxingproductperformance[_data]})
                else:
                    result_list = list(result_dict[_data])
                    result_list.append(Lingxingproductperformance[_data][0])
                    result_dict.update({_data:result_list})
        return result_dict

    def main(self):
        # 遍历get_data数据，拼接路径+key+xlsx进行读取，然后录入。读取失败的跳过
        all_data = self.get_data(start_data="2025-02-18",end_data="2025-02-28")
        for _data in all_data:
            try:
                df = pd.read_excel(f"C:\\Project\\Zlwl\\PMC\\static\\msku_files\\{_data}.xlsx")
            except:
                print(_data)
                continue
            for _data_1 in all_data[_data]:
                new_row = [_data_1["日期"],_data_1["销量"],_data_1["大类排名"],_data_1["广告花费"]]
                df.loc[len(df)] = new_row
            df.to_excel(f"C:\\Project\\Zlwl\\PMC\\static\\msku_files\\{_data}.xlsx",index=False)