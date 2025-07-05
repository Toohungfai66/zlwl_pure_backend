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
        field_names = ["MSKU"]
        if project == "xlyc":
            field_names.append("日期")
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
            datas = {"MSKU":feishu_data["fields"]["MSKU"][0]["text"]}
            if project == "xlyc":
                datas.update({"日期":feishu_data["fields"]["日期"][0]["text"]})
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
        Feishuresult = self.FEISHU_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tblLFvQEaXb3egFw",project="xlyc")
        # 计算上周一的日期
        last_monday = datetime.now() - timedelta(days=datetime.now().weekday() + 7)
        # last_monday = datetime.strptime("2025-05-26", '%Y-%m-%d')
        # 计算上周日的日期
        last_sunday = last_monday + timedelta(days=6)
        # last_sunday = datetime.strptime("2025-06-01", '%Y-%m-%d')
        # 根据上周一到周日的日期获得领星实际销量数据
        Actual_sales_response = lingxingapi().__getSaleStat__(start_date=last_monday.strftime('%Y-%m-%d'), end_date=last_sunday.strftime('%Y-%m-%d'),data_type="3",result_type="1",date_unit="4")
        update_data_list = []
        for _data in Feishuresult:
            if Feishuresult[_data]["日期"] != last_monday.strftime('%Y.%m.%d') + "-" + last_sunday.strftime('%Y.%m.%d'):
                continue
            fields = {"实际销量":0}
            for _data_1 in Actual_sales_response:
                if len(_data_1["msku"]) == 0:
                    continue
                if _data_1["msku"][0] != Feishuresult[_data]["MSKU"]:
                    continue
                fields = {"实际销量":int(_data_1["volumeTotal"])}
                break
            update_data_list.append({"fields":fields,"record_id":_data})
        for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
            payload_dict = {"records":_data}
            print(feishuapi().__postUpdatesDatas__(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tblLFvQEaXb3egFw", payload_dict = payload_dict))

    def get_Year_sales(self):
        feishuresult = self.FEISHU_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tblLFvQEaXb3egFw")
        BM_Msku_list = list(set([feishuresult[x]["MSKU"] for x in feishuresult]))
        # 获取未来第12周的周一与周日日期
        monday = datetime.now() - timedelta(days=datetime.now().weekday())
        next_monday = monday + timedelta(weeks=7)
        next_sunday = next_monday + timedelta(days=6)
        # 根据上一年日期获取同比销量
        Year_sales_response = lingxingapi().__getSaleStat__(start_date=self.get_one_year_ago(next_monday.strftime('%Y.%m.%d')).replace(".","-"), end_date=self.get_one_year_ago(next_sunday.strftime('%Y.%m.%d')).replace(".","-"),data_type="3",result_type="1",date_unit="4")
        insert_data_list = []
        for _data in BM_Msku_list:
            fields = {
                "MSKU":_data,
                "同比销量":0,
                "日期":next_monday.strftime('%Y.%m.%d') + "-" + next_sunday.strftime('%Y.%m.%d')
                }
            for _data_1 in Year_sales_response:
                if _data_1["msku"] == _data:
                    fields.update({"同比销量":int(_data_1["volumeTotal"])})
            insert_data_list.append({"fields":fields})
        for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
            payload_dict = {"records":_data}
            print(feishuapi().__insertBitableDatas__(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tblLFvQEaXb3egFw", payload_dict = payload_dict))

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
        for i in range(1, 7):
            next_monday = monday + timedelta(weeks=i)
            next_sunday = next_monday + timedelta(days=6)
            ok.append(next_monday.strftime('%Y.%m.%d') + "-" + next_sunday.strftime('%Y.%m.%d'))
        return ok
    
    def get_listing_model(self):
        feishuresult_SP = self.FEISHU_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tblWOZnl245oOkJj")
        feishuresult_BM = self.FEISHU_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tblLFvQEaXb3egFw")
        SP_Msku_list = [feishuresult_SP[x]["MSKU"] for x in feishuresult_SP]
        BM_Msku_list = [feishuresult_BM[x]["MSKU"] for x in feishuresult_BM]
        # 获取不在线商品
        delete_Msku_set = set(BM_Msku_list) - set(SP_Msku_list)
        # 获取新增的在线商品
        inset_Msku_set = set(SP_Msku_list) - set(BM_Msku_list)
        # 删除不在线商品
        delete_data_list = []
        for _data in feishuresult_BM:
            if feishuresult_BM[_data]["MSKU"] in delete_Msku_set:
                delete_data_list.append(_data)
        if len(delete_data_list) != 0:
            for _data_1 in [delete_data_list[i:i + 500] for i in range(0, len(delete_data_list), 500)]:
                payload_dict = {"records":_data_1}
                feishuapi().__deleteBitableDatas__(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tblLFvQEaXb3egFw", payload_dict = payload_dict)
        # 判断是否存在新增，没有的话则退出函数
        if len(inset_Msku_set) == 0:
            return True
        # 获取未来8周的同比销量
        result_dict = {}
        for _date in self.get_weekly_dates():
            response = lingxingapi().__getSaleStat__(start_date=self.get_one_year_ago(str(_date).split("-")[0]).replace(".","-"), end_date=self.get_one_year_ago(str(_date).split("-")[1]).replace(".","-"),data_type="3",result_type="1",date_unit="4")
            for _data_1 in response:
                if len(_data_1["msku"]) == 0:
                    continue
                if _date not in result_dict:
                    result_dict.update({_date:[{"MSKU":_data_1["msku"][0],"同比销量":int(_data_1["volumeTotal"])}]}) 
                else:
                    data_1 = result_dict[_date] + [{"MSKU":_data_1["msku"][0],"同比销量":int(_data_1["volumeTotal"])}]
                    result_dict.update({_date:data_1})      
        # 新增
        insert_data_list = []
        for _data in inset_Msku_set:
            for _date in result_dict:
                fields = {
                    "MSKU":_data,
                    "同比销量":0,
                    "日期":_date
                }
                for _data_3 in result_dict[_date]:
                    if _data_3["MSKU"] == _data:
                        fields.update({"同比销量":_data_3["同比销量"]})
                insert_data_list.append({"fields":fields})
        for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
            payload_dict = {"records":_data}
            print(feishuapi().__insertBitableDatas__(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tblLFvQEaXb3egFw", payload_dict = payload_dict))

    def main(self):
        self.get_listing_model()
        self.get_Year_sales()
        self.get_Actual_sales()