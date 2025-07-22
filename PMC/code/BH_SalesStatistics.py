from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta  
import json
import requests
import time
from dateutil.relativedelta import relativedelta

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

    def FEISHU_DICT(self,app_token,table_id,project = "") -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        if project == "FBA":
            field_names = ["父ASIN","店铺","长期供货天数","短期供货天数","总库存金额(FBA)"]
        else:
            field_names = ["父ASIN","店铺","负责人","具体负责人","成交价","FBA可售","FBA在途","FBA调拨","FBA计划入库"]
            if project == "xlyc":
                field_names.append("日期")
                field_names.pop(field_names.index("成交价"))
                field_names.append("最低成交价")
                field_names.append("最高成交价")
        while has_more:
            filter_condition = {
                "field_names": field_names,
                "filter": {
                    "conjunction": "and",
                    "conditions": []
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = app_token, table_id = table_id, page_token = page_token, filter_condition=filter_condition, page_size=500)
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
            if "父ASIN" not in feishu_data["fields"] or "店铺" not in feishu_data["fields"]:
                continue
            if project == "FBA":
                datas = {"父ASIN":feishu_data["fields"]["父ASIN"][0]["text"],"店铺":feishu_data["fields"]["店铺"]["value"][0]["text"]}
                if "长期供货天数" in feishu_data["fields"]:
                    datas["长期供货天数"] = feishu_data["fields"]["长期供货天数"]
                else:
                    datas["长期供货天数"] = 0
                if "短期供货天数" in feishu_data["fields"]:
                    datas["短期供货天数"] = feishu_data["fields"]["短期供货天数"]
                else:
                    datas["短期供货天数"] = 0
                if "总库存金额(FBA)" in feishu_data["fields"]:
                    datas["总库存金额(FBA)"] = feishu_data["fields"]["总库存金额(FBA)"]
                else:
                    datas["总库存金额(FBA)"] = 0
            else:
                datas = {"父ASIN":feishu_data["fields"]["父ASIN"][0]["text"],"店铺":feishu_data["fields"]["店铺"][0]["text"]}
                if project == "xlyc":
                    datas.update({"日期":feishu_data["fields"]["日期"][0]["text"]})
                if "负责人" in feishu_data["fields"]:
                    datas["负责人"] = feishu_data["fields"]["负责人"][0]["name"]
                else:
                    datas["负责人"] = ""
                if "具体负责人" in feishu_data["fields"]:
                    datas["具体负责人"] = feishu_data["fields"]["具体负责人"][0]["text"]
                else:
                    datas["具体负责人"] = ""
                if "成交价" in feishu_data["fields"]:
                    datas["成交价"] = feishu_data["fields"]["成交价"]
                else:
                    datas["成交价"] = 0
                if "FBA可售" in feishu_data["fields"]:
                    datas["FBA可售"] = feishu_data["fields"]["FBA可售"]
                else:
                    datas["FBA可售"] = 0
                if "FBA在途" in feishu_data["fields"]:
                    datas["FBA在途"] = feishu_data["fields"]["FBA在途"]
                else:
                    datas["FBA在途"] = 0
                if "FBA调拨" in feishu_data["fields"]:
                    datas["FBA调拨"] = feishu_data["fields"]["FBA调拨"]
                else:
                    datas["FBA调拨"] = 0
                if "FBA计划入库" in feishu_data["fields"]:
                    datas["FBA计划入库"] = feishu_data["fields"]["FBA计划入库"]
                else:
                    datas["FBA计划入库"] = 0
            result_dict.update({feishu_data["record_id"]:datas})
        return result_dict
    
    def get_one_year_ago(self,date_str):
        # 将输入的日期字符串转换为日期对象
        date_obj = datetime.strptime(date_str, '%Y.%m.%d')
        # 计算一年前的日期
        one_year_ago = date_obj - relativedelta(years=1)
        # 将日期对象转换为字符串
        one_year_ago_str = one_year_ago.strftime('%Y.%m.%d')
        return one_year_ago_str

    def get_Actual_sales(self):
        # 计算上周一的日期
        last_monday = datetime.now() - timedelta(days=datetime.now().weekday() + 7)
        last_monday = datetime.strptime("2025-07-14", '%Y-%m-%d')
        # 计算上周日的日期
        last_sunday = last_monday + timedelta(days=6)
        last_sunday = datetime.strptime("2025-07-20", '%Y-%m-%d')
        # 根据上周一到周日的日期获得领星实际销量数据
        Actual_sales_response = lingxingapi().__getSalesStatistics__(start_date=last_monday.strftime('%Y-%m-%d'), end_date=last_sunday.strftime('%Y-%m-%d'))
        result_dict = {
            "事业一部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tblZfMM49mxJjoaX",
            },"事业二部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tblsYM9fjAqtaq0h",
            },"事业三部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tblFZ2wocAMljZ5m",
            },"事业四部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tbl3o8PwMlTsAGdv",
            },"事业五部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tbleE0SDumXNLLAe",
            },"事业六部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tblyD4f81VxbAXHx",
            },"事业八部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tblsmKm5K61c2b5I",
            },"事业九部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tblvmu45KnNtfS6g",
            },"事业十部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tblTz9Z3yR1s7aRi",
            }}
        listing_dict = {}
        FBA_dict = {}
        Feishuresult_listing = self.FEISHU_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tbl4cEZVqzSo83zl")
        FBA_feishuresult = self.FEISHU_DICT(app_token="XHQPbO5yxay4EysVhf1cdbRanbK",table_id="tblRj9eCz4hEJXPy",project="FBA")
        for _data in Feishuresult_listing:
            if Feishuresult_listing[_data]["父ASIN"] + "|" + Feishuresult_listing[_data]["店铺"] not in listing_dict:
                listing_dict.update({Feishuresult_listing[_data]["父ASIN"] + "|" + Feishuresult_listing[_data]["店铺"]:{"ZGCJJ":Feishuresult_listing[_data]["成交价"],"ZDCJJ":Feishuresult_listing[_data]["成交价"],"FBAKS":Feishuresult_listing[_data]["FBA可售"],"FBADB":Feishuresult_listing[_data]["FBA调拨"],"FBAZT":Feishuresult_listing[_data]["FBA在途"],"FBAJHRK":Feishuresult_listing[_data]["FBA计划入库"]}})
            else:
                if Feishuresult_listing[_data]["成交价"] > listing_dict[Feishuresult_listing[_data]["父ASIN"] + "|" + Feishuresult_listing[_data]["店铺"]]["ZGCJJ"]:
                    ZGCJJ = Feishuresult_listing[_data]["成交价"]
                else:
                    ZGCJJ = listing_dict[Feishuresult_listing[_data]["父ASIN"] + "|" + Feishuresult_listing[_data]["店铺"]]["ZGCJJ"]
                if Feishuresult_listing[_data]["成交价"] < listing_dict[Feishuresult_listing[_data]["父ASIN"] + "|" + Feishuresult_listing[_data]["店铺"]]["ZDCJJ"]:
                    ZDCJJ = Feishuresult_listing[_data]["成交价"]
                else:
                    ZDCJJ = listing_dict[Feishuresult_listing[_data]["父ASIN"] + "|" + Feishuresult_listing[_data]["店铺"]]["ZDCJJ"]
                listing_dict[Feishuresult_listing[_data]["父ASIN"] + "|" + Feishuresult_listing[_data]["店铺"]] = {
                    "ZGCJJ":ZGCJJ,
                    "ZDCJJ":ZDCJJ,
                    "FBAKS":Feishuresult_listing[_data]["FBA可售"] + listing_dict[Feishuresult_listing[_data]["父ASIN"] + "|" + Feishuresult_listing[_data]["店铺"]]["FBAKS"],
                    "FBADB":Feishuresult_listing[_data]["FBA调拨"] + listing_dict[Feishuresult_listing[_data]["父ASIN"] + "|" + Feishuresult_listing[_data]["店铺"]]["FBADB"],
                    "FBAZT":Feishuresult_listing[_data]["FBA在途"] + listing_dict[Feishuresult_listing[_data]["父ASIN"] + "|" + Feishuresult_listing[_data]["店铺"]]["FBAZT"],
                    "FBAJHRK":Feishuresult_listing[_data]["FBA计划入库"] + listing_dict[Feishuresult_listing[_data]["父ASIN"] + "|" + Feishuresult_listing[_data]["店铺"]]["FBAJHRK"]
                }

        for _data in FBA_feishuresult:
            if FBA_feishuresult[_data]["父ASIN"] + "|" + FBA_feishuresult[_data]["店铺"] not in FBA_dict:
                FBA_dict.update({FBA_feishuresult[_data]["父ASIN"] + "|" + FBA_feishuresult[_data]["店铺"]:{"CQ":FBA_feishuresult[_data]["长期供货天数"],"DQ":FBA_feishuresult[_data]["短期供货天数"],"HZ":FBA_feishuresult[_data]["总库存金额(FBA)"]}})
            else:
                FBA_dict[FBA_feishuresult[_data]["父ASIN"] + "|" + FBA_feishuresult[_data]["店铺"]] = {
                    "CQ":(FBA_feishuresult[_data]["长期供货天数"] + FBA_dict[FBA_feishuresult[_data]["父ASIN"] + "|" + FBA_feishuresult[_data]["店铺"]]["CQ"])/2,
                    "DQ":(FBA_feishuresult[_data]["短期供货天数"] + FBA_dict[FBA_feishuresult[_data]["父ASIN"] + "|" + FBA_feishuresult[_data]["店铺"]]["DQ"])/2,
                    "HZ":(FBA_feishuresult[_data]["总库存金额(FBA)"] + FBA_dict[FBA_feishuresult[_data]["父ASIN"] + "|" + FBA_feishuresult[_data]["店铺"]]["HZ"])
                }

        for _data in result_dict:
            update_data_list = []
            Feishuresult = self.FEISHU_DICT(app_token=result_dict[_data]["app_token"],table_id=result_dict[_data]["table_id"],project="xlyc")
            Feishuresult_dict_2 = {}
            for _data_1 in Feishuresult:
                if Feishuresult[_data_1]["日期"] != last_monday.strftime('%Y.%m.%d') + "-" +last_sunday.strftime('%Y.%m.%d'):
                    continue
                if Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"] in listing_dict:
                    Feishuresult_dict_2.update({Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]:{"record_id":_data_1,"ZGCJJ":listing_dict[Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]]["ZGCJJ"],"ZDCJJ":listing_dict[Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]]["ZDCJJ"],"FBAKS":listing_dict[Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]]["FBAKS"],"FBADB":listing_dict[Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]]["FBADB"],"FBAZT":listing_dict[Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]]["FBAZT"],"FBAJHRK":listing_dict[Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]]["FBAJHRK"]}})
                else:
                    Feishuresult_dict_2.update({Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]:{"record_id":_data_1,"ZGCJJ":0,"ZDCJJ":0,"FBAKS":0,"FBADB":0,"FBAZT":0,"FBAJHRK":0}})

                ls_data = dict(Feishuresult_dict_2[Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]])
                if Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"] in FBA_dict:
                    ls_data.update({"CQ":FBA_dict[Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]]["CQ"],"DQ":FBA_dict[Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]]["DQ"],"HZ":FBA_dict[Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]]["HZ"]})
                    Feishuresult_dict_2[Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]] = ls_data
                else:
                    ls_data.update({"CQ":0,"DQ":0,"HZ":0})
                    Feishuresult_dict_2[Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]] = ls_data

            zz_list = []
            for _data_1 in Actual_sales_response:
                zz_list.append(_data_1["parentAsin"][0] + "|" + _data_1["store_name"][0])
                if _data_1["parentAsin"][0] + "|" + _data_1["store_name"][0] not in Feishuresult_dict_2:
                    continue
                update_data_list.append({"fields":{"实际销量":int(_data_1["volumeTotal"]),"最高成交价":Feishuresult_dict_2[_data_1["parentAsin"][0] + "|" + _data_1["store_name"][0]]["ZGCJJ"],"最低成交价":Feishuresult_dict_2[_data_1["parentAsin"][0] + "|" + _data_1["store_name"][0]]["ZDCJJ"],"FBA可售":Feishuresult_dict_2[_data_1["parentAsin"][0] + "|" + _data_1["store_name"][0]]["FBAKS"],"FBA调拨":Feishuresult_dict_2[_data_1["parentAsin"][0] + "|" + _data_1["store_name"][0]]["FBADB"],"FBA在途":Feishuresult_dict_2[_data_1["parentAsin"][0] + "|" + _data_1["store_name"][0]]["FBAZT"],"长期供货天数":Feishuresult_dict_2[_data_1["parentAsin"][0] + "|" + _data_1["store_name"][0]]["CQ"],"短期供货天数":Feishuresult_dict_2[_data_1["parentAsin"][0] + "|" + _data_1["store_name"][0]]["DQ"],"货值":Feishuresult_dict_2[_data_1["parentAsin"][0] + "|" + _data_1["store_name"][0]]["HZ"],"FBA计划入库":Feishuresult_dict_2[_data_1["parentAsin"][0] + "|" + _data_1["store_name"][0]]["FBAJHRK"]},"record_id":Feishuresult_dict_2[_data_1["parentAsin"][0] + "|" + _data_1["store_name"][0]]["record_id"]})
            for _data_1 in set(Feishuresult_dict_2) - set(zz_list):
                update_data_list.append({"fields":{"实际销量":0,"最高成交价":0,"最低成交价":0,"FBA可售":0,"FBA调拨":0,"FBA在途":0,"长期供货天数":0,"短期供货天数":0,"货值":0,"FBA计划入库":0},"record_id":Feishuresult_dict_2[_data_1]["record_id"]})

            # 以500为划分，更新回飞书表格，正常的更新
            for _data_1 in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data_1}
                print(feishuapi().__postUpdatesDatas__(app_token = result_dict[_data]["app_token"], table_id = result_dict[_data]["table_id"], payload_dict = payload_dict))

    def get_Year_sales(self):
        name_open_id_dict = {}
        for _data in ["od-027e3daf1d2d45b1cb46cc4ef3bb4f30"]:
            department_response = feishuapi().__getSubDepartmentId__(department_id=_data)
            for _data_1 in department_response["data"]["items"]:
                departmentuser = feishuapi().__getDepartmentalUsers__(payload_dict={"department_id":_data_1["open_department_id"],"page_size":50})
                if "items" not in departmentuser["data"]:
                    continue
                for _data_2 in departmentuser["data"]["items"]:
                    name_open_id_dict[_data_2["name"]] = _data_2["open_id"]

        Listing_feishuresult = self.FEISHU_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tbl4cEZVqzSo83zl")
        Listing_feishuresult_1 = {}
        for _data in Listing_feishuresult:
            if Listing_feishuresult[_data]["父ASIN"]+"|"+Listing_feishuresult[_data]["店铺"] not in Listing_feishuresult_1:
                Listing_feishuresult_1.update({Listing_feishuresult[_data]["父ASIN"]+"|"+Listing_feishuresult[_data]["店铺"]:{"负责人":Listing_feishuresult[_data]["负责人"],"具体负责人":Listing_feishuresult[_data]["具体负责人"]}})
            else:
                if len(Listing_feishuresult_1[Listing_feishuresult[_data]["父ASIN"]+"|"+Listing_feishuresult[_data]["店铺"]]["具体负责人"]) > len(Listing_feishuresult[_data]["具体负责人"]):
                    continue
                else:
                    Listing_feishuresult_1.update({Listing_feishuresult[_data]["父ASIN"]+"|"+Listing_feishuresult[_data]["店铺"]:{"负责人":Listing_feishuresult[_data]["负责人"],"具体负责人":Listing_feishuresult[_data]["具体负责人"]}})
        # 获取未来第12周的周一与周日日期
        monday = datetime.now() - timedelta(days=datetime.now().weekday())
        next_monday = monday + timedelta(weeks=11)
        next_sunday = next_monday + timedelta(days=6)
        # 根据上一年日期获取同比销量
        Year_sales_response = lingxingapi().__getSalesStatistics__(start_date=self.get_one_year_ago(next_monday.strftime('%Y.%m.%d')).replace(".","-"), end_date=self.get_one_year_ago(next_sunday.strftime('%Y.%m.%d')).replace(".","-"))
        datasproductperformance = lingxingapi().__ProductPerformance__(start_date=self.get_one_year_ago(next_monday.strftime('%Y.%m.%d')).replace(".","-"),end_date=self.get_one_year_ago(next_sunday.strftime('%Y.%m.%d')).replace(".","-"),summary_field="parent_asin",currency_code="")
        result_dict = {
            "事业一部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tblZfMM49mxJjoaX",
                "data":[]
            },"事业二部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tblsYM9fjAqtaq0h",
                "data":[]
            },"事业三部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tblFZ2wocAMljZ5m",
                "data":[]
            },"事业四部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tbl3o8PwMlTsAGdv",
                "data":[]
            },"事业五部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tbleE0SDumXNLLAe",
                "data":[]
            },"事业六部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tblyD4f81VxbAXHx",
                "data":[]
            },"事业八部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tblsmKm5K61c2b5I",
                "data":[]
            },"事业九部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tblvmu45KnNtfS6g",
                "data":[]
            },"事业十部":{
                "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                "table_id":"tblTz9Z3yR1s7aRi",
                "data":[]
            }}
        for _data in Listing_feishuresult_1:
            fields = {
                "父ASIN":str(_data).split("|")[0],
                "店铺":str(_data).split("|")[1],
                "具体负责人":Listing_feishuresult_1[_data]["具体负责人"],
                "同比销量":0,
                "同比利润":0,
                "日期":next_monday.strftime('%Y.%m.%d') + "-" + next_sunday.strftime('%Y.%m.%d')
                }
            if Listing_feishuresult_1[_data]["负责人"] in name_open_id_dict:
                fields["负责人"] = [{"id":name_open_id_dict[Listing_feishuresult_1[_data]["负责人"]]}]
            for _data_1 in Year_sales_response:
                if _data != _data_1["parentAsin"][0] + "|" + _data_1["store_name"][0]:
                    continue
                fields.update({"同比销量":int(_data_1["volumeTotal"])})
                break
            for _data_1 in datasproductperformance:
                if _data != _data_1["parent_asins"][0]["parent_asin"] + "|" + _data_1["seller_store_countries"][0]["seller_name"]:
                    continue
                fields.update({"同比利润":float(_data_1["predict_gross_profit"])})
                break
            for _data_1 in result_dict:
                if _data_1 not in Listing_feishuresult_1[_data]["具体负责人"]:
                    continue
                result_dict[_data_1]["data"] = result_dict[_data_1]["data"] + [{"fields":fields}]
                break
        for _data in result_dict:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data_1 in [result_dict[_data]["data"][i:i + 500] for i in range(0, len(result_dict[_data]["data"]), 500)]:
                payload_dict = {"records":_data_1}
                print(feishuapi().__insertBitableDatas__(app_token = result_dict[_data]["app_token"], table_id = result_dict[_data]["table_id"], payload_dict = payload_dict))

    def get_weekly_dates(self):
        ok = []
        # 获取当前日期
        today = datetime.now()
        # 计算当周周一的日期
        monday = today - timedelta(days=today.weekday())
        # 计算当周周日的日期
        sunday = monday + timedelta(days=6)

        ok.append(monday.strftime('%Y.%m.%d') + "-" + sunday.strftime('%Y.%m.%d'))

        # 计算未来十一周的周一和周日的日期
        for i in range(1, 11):
            next_monday = monday + timedelta(weeks=i)
            next_sunday = next_monday + timedelta(days=6)
            ok.append(next_monday.strftime('%Y.%m.%d') + "-" + next_sunday.strftime('%Y.%m.%d'))

        return ok
    def get_listing_model(self):
        name_open_id_dict = {}
        for _data in ["od-027e3daf1d2d45b1cb46cc4ef3bb4f30"]:
            department_response = feishuapi().__getSubDepartmentId__(department_id=_data)
            for _data_1 in department_response["data"]["items"]:
                departmentuser = feishuapi().__getDepartmentalUsers__(payload_dict={"department_id":_data_1["open_department_id"],"page_size":50})
                if "items" not in departmentuser["data"]:
                    continue
                for _data_2 in departmentuser["data"]["items"]:
                    name_open_id_dict[_data_2["name"]] = _data_2["open_id"]
        listing_feishuresult = self.FEISHU_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tbl4cEZVqzSo83zl")
        listing_key_dict = {"事业一部":[],"事业二部":[],"事业三部":[],"事业四部":[],"事业五部":[],"事业六部":[],"事业八部":[],"事业九部":[],"事业十部":[]}
        xx_dict = {}
        for _data in listing_feishuresult:
            if "事业一部" in listing_feishuresult[_data]["具体负责人"]:
                listing_key_dict.update({"事业一部":list(set(listing_key_dict["事业一部"] + [listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]]))})
                xx_dict.update({listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]:{"负责人":listing_feishuresult[_data]["负责人"],"具体负责人":listing_feishuresult[_data]["具体负责人"]}})
            elif "事业二部" in listing_feishuresult[_data]["具体负责人"]:
                listing_key_dict.update({"事业二部":list(set(listing_key_dict["事业二部"] + [listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]]))})
                xx_dict.update({listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]:{"负责人":listing_feishuresult[_data]["负责人"],"具体负责人":listing_feishuresult[_data]["具体负责人"]}})
            elif "事业三部" in listing_feishuresult[_data]["具体负责人"]:
                listing_key_dict.update({"事业三部":list(set(listing_key_dict["事业三部"] + [listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]]))})
                xx_dict.update({listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]:{"负责人":listing_feishuresult[_data]["负责人"],"具体负责人":listing_feishuresult[_data]["具体负责人"]}})
            elif "事业四部" in listing_feishuresult[_data]["具体负责人"]:
                listing_key_dict.update({"事业四部":list(set(listing_key_dict["事业四部"] + [listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]]))})
                xx_dict.update({listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]:{"负责人":listing_feishuresult[_data]["负责人"],"具体负责人":listing_feishuresult[_data]["具体负责人"]}})
            elif "事业五部" in listing_feishuresult[_data]["具体负责人"]:
                listing_key_dict.update({"事业五部":list(set(listing_key_dict["事业五部"] + [listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]]))})
                xx_dict.update({listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]:{"负责人":listing_feishuresult[_data]["负责人"],"具体负责人":listing_feishuresult[_data]["具体负责人"]}})
            elif "事业六部" in listing_feishuresult[_data]["具体负责人"]:
                listing_key_dict.update({"事业六部":list(set(listing_key_dict["事业六部"] + [listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]]))})
                xx_dict.update({listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]:{"负责人":listing_feishuresult[_data]["负责人"],"具体负责人":listing_feishuresult[_data]["具体负责人"]}})
            elif "事业八部" in listing_feishuresult[_data]["具体负责人"]:
                listing_key_dict.update({"事业八部":list(set(listing_key_dict["事业八部"] + [listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]]))})
                xx_dict.update({listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]:{"负责人":listing_feishuresult[_data]["负责人"],"具体负责人":listing_feishuresult[_data]["具体负责人"]}})
            elif "事业九部" in listing_feishuresult[_data]["具体负责人"]:
                listing_key_dict.update({"事业九部":list(set(listing_key_dict["事业九部"] + [listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]]))})
                xx_dict.update({listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]:{"负责人":listing_feishuresult[_data]["负责人"],"具体负责人":listing_feishuresult[_data]["具体负责人"]}})
            elif "事业十部" in listing_feishuresult[_data]["具体负责人"]:
                listing_key_dict.update({"事业十部":list(set(listing_key_dict["事业十部"] + [listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]]))})
                xx_dict.update({listing_feishuresult[_data]["父ASIN"] + "|" + listing_feishuresult[_data]["店铺"]:{"负责人":listing_feishuresult[_data]["负责人"],"具体负责人":listing_feishuresult[_data]["具体负责人"]}})
            else:
                continue
        result_dict = {}
        result_dict_1 = {}
        for _date in self.get_weekly_dates():
            response = lingxingapi().__getSalesStatistics__(start_date=self.get_one_year_ago(str(_date).split("-")[0]).replace(".","-"), end_date=self.get_one_year_ago(str(_date).split("-")[1]).replace(".","-"))
            response_1 = lingxingapi().__ProductPerformance__(start_date=self.get_one_year_ago(str(_date).split("-")[0]).replace(".","-"),end_date=self.get_one_year_ago(str(_date).split("-")[1]).replace(".","-"),summary_field="parent_asin",currency_code="")
            for _data_1 in response:
                if _date not in result_dict:
                    result_dict.update({_date:[{"父ASIN":_data_1["parentAsin"][0],"店铺":_data_1["store_name"][0],"同比销量":int(_data_1["volumeTotal"])}]}) 
                else:
                    data_1 = result_dict[_date] + [{"父ASIN":_data_1["parentAsin"][0],"店铺":_data_1["store_name"][0],"同比销量":int(_data_1["volumeTotal"])}]
                    result_dict.update({_date:data_1})      
            for _data_1 in response_1:
                if _date not in result_dict_1:
                    result_dict_1.update({_date:[{"父ASIN":_data_1["parent_asins"][0]["parent_asin"],"店铺":_data_1["seller_store_countries"][0]["seller_name"],"同比利润":float(_data_1["predict_gross_profit"])}]}) 
                else:
                    data_1 = result_dict_1[_date] + [{"父ASIN":_data_1["parent_asins"][0]["parent_asin"],"店铺":_data_1["seller_store_countries"][0]["seller_name"],"同比利润":float(_data_1["predict_gross_profit"])}]
                    result_dict_1.update({_date:data_1})    
        for _data in listing_key_dict:
            if _data == "事业一部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tblZfMM49mxJjoaX"
            elif _data == "事业二部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tblsYM9fjAqtaq0h"
            elif _data == "事业三部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tblFZ2wocAMljZ5m"
            elif _data == "事业四部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tbl3o8PwMlTsAGdv"
            elif _data == "事业五部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tbleE0SDumXNLLAe"
            elif _data == "事业六部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tblyD4f81VxbAXHx"
            elif _data == "事业八部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tblsmKm5K61c2b5I"
            elif _data == "事业九部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tblvmu45KnNtfS6g"
            elif _data == "事业十部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tblTz9Z3yR1s7aRi"
            else:
                continue
            feishuresult = self.FEISHU_DICT(app_token=app_token,table_id=table_id,project="xlyc")
            key_list = set([feishuresult[_data_1]["父ASIN"] + "|" + feishuresult[_data_1]["店铺"] for _data_1 in feishuresult])

            newupdate_data = list(set(listing_key_dict[_data]) - key_list)
            delete_data = list(key_list - set(listing_key_dict[_data]))

            if len(delete_data) != 0:
                delete_data_list = []
                for _data_1 in feishuresult:
                    if feishuresult[_data_1]["父ASIN"] + "|" + feishuresult[_data_1]["店铺"] in delete_data:
                        delete_data_list.append(_data_1)
                for _data_1 in [delete_data_list[i:i + 500] for i in range(0, len(delete_data_list), 500)]:
                    payload_dict = {"records":_data_1}
                    feishuapi().__deleteBitableDatas__(app_token = app_token, table_id = table_id, payload_dict = payload_dict)

            if len(newupdate_data) != 0:
                insert_data_list = []
                for _data_2 in newupdate_data:
                    for _date in result_dict:
                        fields = {
                            "父ASIN":str(_data_2).split("|")[0],
                            "店铺":str(_data_2).split("|")[1],
                            "具体负责人":xx_dict[_data_2]["具体负责人"],
                            "同比销量":0,
                            "日期":_date
                        }
                        if xx_dict[_data_2]["负责人"] in name_open_id_dict:
                            fields["负责人"] = [{"id":name_open_id_dict[xx_dict[_data_2]["负责人"]]}]
                        for _data_3 in result_dict[_date]:
                            if _data_3["父ASIN"] == None or _data_3["店铺"] == None:
                                continue
                            if _data_3["父ASIN"] + "|" + _data_3["店铺"] != _data_2:
                                continue
                            fields.update({"同比销量":_data_3["同比销量"]})
                        for _data_3 in result_dict_1[_date]:
                            if _data_3["父ASIN"] == None or _data_3["店铺"] == None:
                                continue
                            if _data_3["父ASIN"] + "|" + _data_3["店铺"] != _data_2:
                                continue
                            fields.update({"同比利润":_data_3["同比利润"]})
                        insert_data_list.append({"fields":fields})

                for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
                    payload_dict = {"records":_data}
                    print(feishuapi().__insertBitableDatas__(app_token = app_token, table_id = table_id, payload_dict = payload_dict))


    def CS(self):
        # 获取未来第12周的周一与周日日期
        for i in [
            [datetime.strptime("2025-04-21", '%Y-%m-%d'),datetime.strptime("2025-04-27", '%Y-%m-%d')],
            [datetime.strptime("2025-04-28", '%Y-%m-%d'),datetime.strptime("2025-05-04", '%Y-%m-%d')],
            [datetime.strptime("2025-05-05", '%Y-%m-%d'),datetime.strptime("2025-05-11", '%Y-%m-%d')],
            [datetime.strptime("2025-05-12", '%Y-%m-%d'),datetime.strptime("2025-05-18", '%Y-%m-%d')],
            [datetime.strptime("2025-05-19", '%Y-%m-%d'),datetime.strptime("2025-05-25", '%Y-%m-%d')],
            [datetime.strptime("2025-05-26", '%Y-%m-%d'),datetime.strptime("2025-06-01", '%Y-%m-%d')],
            [datetime.strptime("2025-06-02", '%Y-%m-%d'),datetime.strptime("2025-06-08", '%Y-%m-%d')],
            [datetime.strptime("2025-06-09", '%Y-%m-%d'),datetime.strptime("2025-06-15", '%Y-%m-%d')],
            [datetime.strptime("2025-06-16", '%Y-%m-%d'),datetime.strptime("2025-06-22", '%Y-%m-%d')],
            [datetime.strptime("2025-06-23", '%Y-%m-%d'),datetime.strptime("2025-06-29", '%Y-%m-%d')],
            [datetime.strptime("2025-06-30", '%Y-%m-%d'),datetime.strptime("2025-07-06", '%Y-%m-%d')],
            [datetime.strptime("2025-07-07", '%Y-%m-%d'),datetime.strptime("2025-07-13", '%Y-%m-%d')],
            [datetime.strptime("2025-07-14", '%Y-%m-%d'),datetime.strptime("2025-07-20", '%Y-%m-%d')],
            [datetime.strptime("2025-07-21", '%Y-%m-%d'),datetime.strptime("2025-07-27", '%Y-%m-%d')],
            [datetime.strptime("2025-07-28", '%Y-%m-%d'),datetime.strptime("2025-08-03", '%Y-%m-%d')],
            [datetime.strptime("2025-08-04", '%Y-%m-%d'),datetime.strptime("2025-08-10", '%Y-%m-%d')],
            [datetime.strptime("2025-08-11", '%Y-%m-%d'),datetime.strptime("2025-08-17", '%Y-%m-%d')],
            [datetime.strptime("2025-08-18", '%Y-%m-%d'),datetime.strptime("2025-08-24", '%Y-%m-%d')],
            [datetime.strptime("2025-08-25", '%Y-%m-%d'),datetime.strptime("2025-08-31", '%Y-%m-%d')],
            [datetime.strptime("2025-09-01", '%Y-%m-%d'),datetime.strptime("2025-09-07", '%Y-%m-%d')],
            [datetime.strptime("2025-09-08", '%Y-%m-%d'),datetime.strptime("2025-09-14", '%Y-%m-%d')],
            [datetime.strptime("2025-09-15", '%Y-%m-%d'),datetime.strptime("2025-09-21", '%Y-%m-%d')],
            [datetime.strptime("2025-09-22", '%Y-%m-%d'),datetime.strptime("2025-09-28", '%Y-%m-%d')],
            [datetime.strptime("2025-09-29", '%Y-%m-%d'),datetime.strptime("2025-10-05", '%Y-%m-%d')],
            ]:
            next_monday = i[0]
            next_sunday = i[1]
            datasproductperformance = lingxingapi().__ProductPerformance__(start_date=self.get_one_year_ago(next_monday.strftime('%Y.%m.%d')).replace(".","-"),end_date=self.get_one_year_ago(next_sunday.strftime('%Y.%m.%d')).replace(".","-"),summary_field="parent_asin",currency_code="")
            result_dict = {
                "事业一部":{
                    "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                    "table_id":"tblZfMM49mxJjoaX",
                    "data":[]
                },"事业二部":{
                    "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                    "table_id":"tblsYM9fjAqtaq0h",
                    "data":[]
                },"事业三部":{
                    "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                    "table_id":"tblFZ2wocAMljZ5m",
                    "data":[]
                },"事业四部":{
                    "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                    "table_id":"tbl3o8PwMlTsAGdv",
                    "data":[]
                },"事业五部":{
                    "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                    "table_id":"tbleE0SDumXNLLAe",
                    "data":[]
                },"事业六部":{
                    "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                    "table_id":"tblyD4f81VxbAXHx",
                    "data":[]
                },"事业八部":{
                    "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                    "table_id":"tblsmKm5K61c2b5I",
                    "data":[]
                },"事业九部":{
                    "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                    "table_id":"tblvmu45KnNtfS6g",
                    "data":[]
                },"事业十部":{
                    "app_token":"TxmobrecbaIyblsh9p8cv3k6n3f",
                    "table_id":"tblTz9Z3yR1s7aRi",
                    "data":[]
                }}
            for _data in result_dict:
                update_data_list = []
                feishuresult = self.FEISHU_DICT(app_token=result_dict[_data]["app_token"],table_id=result_dict[_data]["table_id"],project="xlyc")
                datasproductperformance_dict = {}
                for _data_1 in datasproductperformance:
                    datasproductperformance_dict.update({_data_1["parent_asins"][0]["parent_asin"]+_data_1["seller_store_countries"][0]["seller_name"]:float(_data_1["predict_gross_profit"])})
                for _data_1 in feishuresult:
                    if feishuresult[_data_1]["日期"] != next_monday.strftime('%Y.%m.%d') + "-" + next_sunday.strftime('%Y.%m.%d'):
                        continue
                    fields = {
                        "同比利润":0,
                    }
                    if feishuresult[_data_1]["父ASIN"] + feishuresult[_data_1]["店铺"] in datasproductperformance_dict:
                        fields.update({"同比利润":datasproductperformance_dict[feishuresult[_data_1]["父ASIN"] + feishuresult[_data_1]["店铺"]]})
                    update_data_list.append({
                        "fields":fields,
                        "record_id":_data_1
                        })
                # 以500为划分，更新回飞书表格，正常的更新
                for _data_1 in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                    payload_dict = {"records":_data_1}
                    print(feishuapi().__postUpdatesDatas__(app_token = result_dict[_data]["app_token"], table_id = result_dict[_data]["table_id"], payload_dict = payload_dict))

    def main(self):
        # self.get_listing_model()
        # self.get_Year_sales()
        self.get_Actual_sales()
        # self.CS()