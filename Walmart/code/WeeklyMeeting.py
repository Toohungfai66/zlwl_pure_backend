from datetime import datetime, timedelta
from .LingXingAPI import lingxingapi
from .FeiShuAPI import feishuapi
class weeklymeeting:
    def __init__(self):
        pass
    
    def __getDate__(self):
        # 获取当前日期
        today = datetime.now().date()

        # 计算今天是星期几（0=周一，6=周日）
        weekday = today.weekday()

        # 计算上周的周一和周日
        last_monday = today - timedelta(days=weekday + 7)  # 往前推 (当前周几 + 7) 天
        last_sunday = today - timedelta(days=weekday + 1)  # 往前推 (当前周几 + 1) 天

        return {"start_date":last_monday.strftime("%Y-%m-%d"), "end_date":last_sunday.strftime("%Y-%m-%d")}
    
    def main(self):
        date_dict = self.__getDate__()
        # date_dict = {"start_date":"2025-06-16", "end_date":"2025-06-22"}
        lingxingresult = lingxingapi().__getSaleStat__(start_date=date_dict["start_date"],end_date=date_dict["end_date"],result_type="1",date_unit="4",data_type="3")
        lingxingresult_gmv = lingxingapi().__getSaleStat__(start_date=date_dict["start_date"],end_date=date_dict["end_date"],result_type="3",date_unit="4",data_type="3")
        msku_gmv = {}
        for _data in lingxingresult_gmv:
            if len(_data["msku"]) == 0:
                continue
            msku_gmv.update({_data["msku"][0]:float(_data["volumeTotal"])})
        insert_data_list = []
        for _data in lingxingresult:
            if _data["platform_name"][0] != "Walmart":
                continue
            if len(_data["msku"]) == 0:
                continue
            fields = {"MSKU":_data["msku"][0]}
            if len(_data["site_name"]) != 0:
                fields["站点"] =  _data["site_name"][0]
            if len(_data["store_name"]) != 0:
                fields["店铺"] =  _data["store_name"][0]
            if len(_data["sku"]) != 0:
                fields["SKU"] =  _data["sku"][0]
            if len(_data["product_name"]) != 0:
                fields["品名"] =  _data["product_name"][0]
            if _data["msku"][0] in msku_gmv:
                fields["GMV"] = msku_gmv[_data["msku"][0]]
            fields.update({
                # "图片URL":_data["pic_url"],
                "周":date_dict["start_date"] + "~" + date_dict["end_date"],
                "单量":int(_data["volumeTotal"])
            })
            insert_data_list.append({"fields": fields})
        # 2025年6月2周  2025-06-02~2025-06-08
        if len(insert_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
                payload_dict = {"records":_data}
                print(feishuapi().__insertBitableDatas__(app_token = 'XNSibj8OoannacsvVbjcRQREnGg', table_id = 'tblymYFizVQFo9hK', payload_dict = payload_dict))
