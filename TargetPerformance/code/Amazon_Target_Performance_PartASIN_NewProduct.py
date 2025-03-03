import requests
import json
from urllib.parse import unquote
from datetime import datetime, timedelta  
from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi

class amazon_target_performance_partASIN_newproduct:

    def __init__(self) -> None:
        pass

    def get_dates_last_week(self, str_date:str) -> list:
        today = datetime.strptime(str_date,"%Y-%m-%d")
        # 计算本周的周几（0表示周一，6表示周日）
        weekday_today = today.weekday()
        # 找到上周日的日期
        last_sunday = today - timedelta(days=weekday_today + 1)
        dates = []
        for i in range(7):
            date = last_sunday + timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))
        return dates

    def get_dates_since_last_sunday(self, str_date:str) -> list:  
        today = datetime.strptime(str_date,"%Y-%m-%d")
        today_weekday = today.weekday()
        last_sunday = today - timedelta(days=today_weekday + 1) if today_weekday != 6 else today   
        dates = [(last_sunday + timedelta(days=i)).date() for i in range((today - last_sunday).days + 1)]  
        return dates  

    def get_bitable_datas(self, app_token, table_id, filter_condition, page_token='', page_size=20) -> json:

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search?page_size={page_size}&page_token={page_token}&user_id_type=user_id"
        payload = json.dumps(filter_condition)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {feishuapi().__getTenantAccessToken__()}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()

    def FEISHU_LIRUN_DICT(self, lxzq:str) -> list:
        page_token = ''
        has_more = True
        feishu_datas = []
        while has_more:
            filter_condition = {
                "field_names": [
                    "父ASIN",
                    "国家"
                ],
                "filter": {
                    "conjunction": "and",
                    "conditions": [
                    {
                        "field_name": "领星周期",
                        "operator": "is",
                        "value": [
                        lxzq
                        ]
                    }
                    ]
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = 'MGCzb9OGkaujmysIe8cc6WpwnSd', table_id = 'tbl00A23bwvlJg4x', filter_condition=filter_condition, page_token = page_token, page_size=500)
            if response['code'] == 0:
                has_more = response['data']['has_more']
                if has_more == False:
                    feishu_datas.extend(response['data']['items'])
                    break
                page_token = response['data']['page_token']
                feishu_datas.extend(response['data']['items'])
            else:
                raise Exception(response['msg'])
        result_dict= {}
        for feishu_data in feishu_datas:
            result_dict.update({feishu_data["fields"]["父ASIN"][0]["text"]+","+feishu_data["fields"]["国家"][0]["text"]:feishu_data["record_id"]})
        return result_dict
    def main(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        # 获取当天位于当周的的起始日期
        Lx_datetime_weeks = self.get_dates_since_last_sunday(str_date = date_str)
        dates_last_week = self.get_dates_last_week(str_date = date_str)  
        start_yesterday_str = Lx_datetime_weeks[0].strftime('%Y-%m-%d')
        start_yesterday_end = Lx_datetime_weeks[-1].strftime('%Y-%m-%d')

        # 获取利润报表数据
        datasstatementprofit = lingxingapi().__StatementProfitParentASIN__(startDate=start_yesterday_str, endDate=start_yesterday_end)
        LingxingProfitResult = {}
        for _data in datasstatementprofit:
            if len(_data["parentAsin"])==0:
                continue
            if type(_data["country"]) == list:
                country = ""
                for _data_1 in _data["country"]:
                    country = country + _data_1  + ","
                country = country[:-1]
            else:
                country = _data["country"]
            LingxingProfitResult.update({
                _data["parentAsin"] + "," + country:{
                    "totalSalesQuantity":_data["totalSalesQuantity"], # 销量
                    "totalSalesAmount":_data["totalSalesAmount"], # 销售额
                    "SR":_data["totalSalesAmount"] + _data["shippingCredits"] + _data["promotionalRebates"] + _data["fbaInventoryCredit"] + _data["otherInAmount"] + _data["totalSalesRefunds"] + _data["totalFeeRefunds"],# 收入  销售额 + 买家运费 + 促销折扣 + FBA库存赔偿 + 其他收入 + 收入退款额 + 费用退款额
                    "grossProfit":_data["grossProfit"], # 毛利润
                }
            })
        # 获取产品表现数据
        datasproductperformance = lingxingapi().__ProductPerformance__(start_date=start_yesterday_str, end_date=start_yesterday_end)
        Lingxingproductperformance = {}
        for _data in datasproductperformance:
            if _data["cate_rank"] == None:
                _data["cate_rank"] = 0
            if _data["small_cate_rank"] == None:
                _data["small_cate_rank"] = [{"rank":0}]
            if _data["cvr"] == None:
                _data["cvr"] = 0
            if _data["acos"] == None:
                _data["acos"] = 0
            if _data["acoas"] == None:
                _data["acoas"] = 0
            if _data["cpo"] == None:
                _data["cpo"] = 0
            if _data["order_items"] == None:
                _data["order_items"] = 0
            if _data["ad_order_quantity"] == None:
                _data["ad_order_quantity"] = 0
            Lingxingproductdict = {
                    _data["parent_asins"][0]["parent_asin"] + "," + _data["seller_store_countries"][0]["country"]:{
                        "cate_rank":_data["cate_rank"], # 大类排名
                        "small_cate_rank":_data["small_cate_rank"][0]["rank"], # 小类排名
                        "cvr":float(_data["cvr"]), # cvr
                        "acos":float(_data["acos"]), # acos
                        "acoas":float(_data["acoas"]), # TACOS
                        "cpo":float(_data["cpo"]), # CPA
                        "order_items":_data["order_items"], # 订单量
                        "ad_order_quantity":_data["ad_order_quantity"] # 广告订单量
                    }
                }
            if _data["parent_asins"][0]["parent_asin"] + "," + _data["seller_store_countries"][0]["country"] not in Lingxingproductperformance:
                Lingxingproductperformance.update(Lingxingproductdict)
            elif Lingxingproductperformance[_data["parent_asins"][0]["parent_asin"] + "," + _data["seller_store_countries"][0]["country"]]["cate_rank"] < _data["cate_rank"]:
                Lingxingproductperformance.update(Lingxingproductdict)
            else:
                continue
        
        # 获取新品源表的所有记录，{父ASIN,国家:ID，....}
        FEISHU_LIRUN_DICT_DICT = self.FEISHU_LIRUN_DICT(lxzq=dates_last_week[0]+"~"+dates_last_week[-1])
        # 取出映射表含有父ASIN国家的利润报表数据，通过循环映射表，因为它是基准
        update_payload_list = []
        insert_payload_list = []
        for _data in LingxingProfitResult:
            fields_dict = {
                "父ASIN":str(_data).split(",")[0],
                "国家":str(_data).split(",")[1],
                "毛利润(实现)":LingxingProfitResult[_data]["grossProfit"], 
                "销量(实现)":LingxingProfitResult[_data]["totalSalesQuantity"],
                "收入(实现)":LingxingProfitResult[_data]["SR"],
            }
            try:
                fields_dict.update({
                    "大类排名(实现)":Lingxingproductperformance[_data]["cate_rank"],
                    "小类排名(实现)":Lingxingproductperformance[_data]["small_cate_rank"],
                    "CVR(实现)":Lingxingproductperformance[_data]["cvr"], 
                    "CPA(实现)":Lingxingproductperformance[_data]["cpo"], 
                    "ACOS(实现)":Lingxingproductperformance[_data]["acos"],
                    "TACOS(实现)":Lingxingproductperformance[_data]["acoas"],
                    "广告订单量":Lingxingproductperformance[_data]["ad_order_quantity"],
                    "自然订单量":Lingxingproductperformance[_data]["order_items"] - Lingxingproductperformance[_data]["ad_order_quantity"]
                    })
            except:
                fields_dict.update({
                    "大类排名(实现)":0,
                    "小类排名(实现)":0,
                    "CVR(实现)":0, 
                    "CPA(实现)":0, 
                    "ACOS(实现)":0,
                    "TACOS(实现)":0,
                    "广告订单量":0,
                    "自然订单量":0,
                    })
            if _data in FEISHU_LIRUN_DICT_DICT:
                update_payload_list.append({"record_id": FEISHU_LIRUN_DICT_DICT[_data], "fields": fields_dict})
            else:
                fields_dict.update({"领星周期":dates_last_week[0]+"~"+dates_last_week[-1]})
                insert_payload_list.append({"fields": fields_dict})

        # 更新数据
        for _data in [update_payload_list[i:i + 500] for i in range(0, len(update_payload_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__postUpdatesDatas__(app_token="MGCzb9OGkaujmysIe8cc6WpwnSd", table_id="tbl00A23bwvlJg4x", payload_dict=payload_dict)

        # 插入数据
        for _data in [insert_payload_list[i:i + 500] for i in range(0, len(insert_payload_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__insertBitableDatas__(app_token = 'MGCzb9OGkaujmysIe8cc6WpwnSd', table_id = 'tbl00A23bwvlJg4x', payload_dict = payload_dict)