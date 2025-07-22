from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta  
import json
import requests

class bh_productperformance:

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

    def FEISHU_FBA_DICT(self, app_token, table_id) -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        field_names = ["父ASIN","店铺","日期"]
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
            result_dict.update({feishu_data["record_id"]:{"父ASIN":feishu_data["fields"]["父ASIN"][0]["text"],"店铺":feishu_data["fields"]["店铺"][0]["text"],"日期":feishu_data["fields"]["日期"][0]["text"]}})
        return result_dict

    def main(self):
        # 计算上周一的日期
        last_monday = datetime.now() - timedelta(days=datetime.now().weekday() + 7)
        # last_monday = datetime.strptime("2025-06-23", '%Y-%m-%d')
        # 计算上周日的日期
        last_sunday = last_monday + timedelta(days=6)
        # last_sunday = datetime.strptime("2025-06-29", '%Y-%m-%d')
        # for i in [
        #           [datetime.strptime("2025-07-07", '%Y-%m-%d'),datetime.strptime("2025-07-13", '%Y-%m-%d')],
        #           [datetime.strptime("2025-06-30", '%Y-%m-%d'),datetime.strptime("2025-07-06", '%Y-%m-%d')],
        #           [datetime.strptime("2025-06-23", '%Y-%m-%d'),datetime.strptime("2025-06-29", '%Y-%m-%d')],
        #           [datetime.strptime("2025-06-16", '%Y-%m-%d'),datetime.strptime("2025-06-22", '%Y-%m-%d')],
        #           [datetime.strptime("2025-06-09", '%Y-%m-%d'),datetime.strptime("2025-06-15", '%Y-%m-%d')],
        #           [datetime.strptime("2025-06-02", '%Y-%m-%d'),datetime.strptime("2025-06-08", '%Y-%m-%d')],
        #           [datetime.strptime("2025-05-26", '%Y-%m-%d'),datetime.strptime("2025-06-01", '%Y-%m-%d')],
        #           [datetime.strptime("2025-05-19", '%Y-%m-%d'),datetime.strptime("2025-05-25", '%Y-%m-%d')],
        #           [datetime.strptime("2025-05-12", '%Y-%m-%d'),datetime.strptime("2025-05-18", '%Y-%m-%d')],
        #           [datetime.strptime("2025-05-05", '%Y-%m-%d'),datetime.strptime("2025-05-11", '%Y-%m-%d')],
        #           [datetime.strptime("2025-04-28", '%Y-%m-%d'),datetime.strptime("2025-05-04", '%Y-%m-%d')],
        #           [datetime.strptime("2025-04-21", '%Y-%m-%d'),datetime.strptime("2025-04-27", '%Y-%m-%d')]]:
        #     last_monday = i[0]
        #     last_sunday = i[1]
        datasproductperformance = lingxingapi().__ProductPerformance__(start_date=last_monday.strftime('%Y-%m-%d'),end_date=last_sunday.strftime('%Y-%m-%d'),summary_field="parent_asin",currency_code="")
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
        for _data in result_dict:
            update_data_list = []
            Feishuresult = self.FEISHU_FBA_DICT(app_token=result_dict[_data]["app_token"],table_id=result_dict[_data]["table_id"])
            Feishuresult_dict_2 = {}
            for _data_1 in Feishuresult:
                if Feishuresult[_data_1]["日期"] != last_monday.strftime('%Y.%m.%d') + "-" +last_sunday.strftime('%Y.%m.%d'):
                    continue
                Feishuresult_dict_2.update({Feishuresult[_data_1]["父ASIN"] + "|" + Feishuresult[_data_1]["店铺"]:_data_1})
            zz_list = []
            for _data_1 in datasproductperformance:
                zz_list.append(_data_1["parent_asins"][0]["parent_asin"] + "|" + _data_1["seller_store_countries"][0]["seller_name"])
                if _data_1["parent_asins"][0]["parent_asin"] + "|" + _data_1["seller_store_countries"][0]["seller_name"] not in Feishuresult_dict_2:
                    continue
                fields = {}
                try:
                    fields["销量环比"] = float(_data_1["volume_chain_ratio"])
                except:
                    fields["销量环比"] = 0
                try:
                    fields["退款量"] = int(_data_1["return_count"])
                except:
                    fields["退款量"] = 0
                try:
                    fields["退货量"] = int(_data_1["return_goods_count"])
                except:
                    fields["退货量"] = 0
                try:
                    fields["ACOS"] = float(_data_1["acos"])
                except:
                    fields["ACOS"] = 0
                try:
                    fields["退款率"] = float(_data_1["return_rate"])
                except:
                    fields["退款率"] = 0
                try:
                    fields["销售额环比"] = float(_data_1["amount_chain_ratio"])
                except:
                    fields["销售额环比"] = 0
                try:
                    fields["广告花费"] = abs(float(_data_1["spend"]))
                except:
                    fields["广告花费"] = 0
                try:
                    fields["退货率"] = float(_data_1["return_goods_rate"])
                except:
                    fields["退货率"] = 0
                try:
                    fields["广告订单量"] = _data_1["ad_order_quantity"]
                except:
                    fields["广告订单量"] = 0
                try:
                    fields["Sessions-Total"] = _data_1["sessions_total"]
                except:
                    fields["Sessions-Total"] = 0
                try:
                    fields["评论数"] = _data_1["reviews_count"]
                except:
                    fields["评论数"] = 0
                try:
                    fields["订单量"] = _data_1["order_items"]
                except:
                    fields["订单量"] = 0
                try:
                    fields["GMV"] = float(_data_1["amount"])
                except:
                    fields["GMV"] = 0
                try:
                    fields["退款金额"] = abs(float(_data_1["return_amount"]))
                except:
                    fields["退款金额"] = 0
                try:
                    fields["评分"] = float(_data_1["avg_star"])
                except:
                    fields["评分"] = 0
                try:
                    fields["结算毛利润"] = float(_data_1["gross_profit"])
                except:
                    fields["结算毛利润"] = 0
                try:
                    fields["订单毛利润"] = float(_data_1["predict_gross_profit"])
                except:
                    fields["订单毛利润"] = 0
                try:
                    fields["小类排名"] = _data_1["small_cate_rank"][0]["rank"]
                except:
                    fields["小类排名"] = 0
                try:
                    fields["大类排名"] = _data_1["cate_rank"]
                except:
                    fields["大类排名"] = 0
                try:
                    fields["广告CVR"] = float(_data_1["ad_cvr"])
                except:
                    fields["广告CVR"] = 0
                try:
                    fields["CTR"] = float(_data_1["ctr"])
                except:
                    fields["CTR"] = 0
                try:
                    fields["TACOS"] = float(_data_1["acoas"])
                except:
                    fields["TACOS"] = 0
                try:
                    fields["CVR"] = float(_data_1["cvr"])
                except:
                    fields["CVR"] = 0
                try:
                    fields["CPO"] = float(_data_1["cpo"])
                except:
                    fields["CPO"] = 0
                try:
                    fields["CPC"] = float(_data_1["cpc"])
                except:
                    fields["CPC"] = 0
                update_data_list.append({
                    "fields":fields,
                    "record_id":Feishuresult_dict_2[_data_1["parent_asins"][0]["parent_asin"] + "|" + _data_1["seller_store_countries"][0]["seller_name"]]
                    })
            for _data_1 in set(Feishuresult_dict_2) - set(zz_list):
                update_data_list.append({
                    "fields":{
                        "GMV":0,
                        "订单量":0,
                        "大类排名":0,
                        "小类排名":0,
                        "退款金额":0,
                        "评分":0,
                        "评论数":0,
                        "结算毛利润":0,
                        "订单毛利润":0,
                        "Sessions-Total":0,
                        "CVR":0,
                        "广告花费":0,
                        "广告订单量":0,
                        "CTR":0,
                        "广告CVR":0,
                        "CPC":0,
                        "TACOS":0,
                        "CPO":0,
                        "销量环比":0,
                        "销售额环比":0,
                        "退款率":0,
                        "退货率":0,
                        "退款量":0,
                        "退货量":0,
                        "ACOS":0
                        },
                    "record_id":Feishuresult_dict_2[_data_1]
                    })
            # 以500为划分，更新回飞书表格，正常的更新
            for _data_1 in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data_1}
                print(feishuapi().__postUpdatesDatas__(app_token = result_dict[_data]["app_token"], table_id = result_dict[_data]["table_id"], payload_dict = payload_dict))