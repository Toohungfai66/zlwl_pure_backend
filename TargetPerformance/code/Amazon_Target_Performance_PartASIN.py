import requests
import json
from urllib.parse import unquote
from datetime import datetime, timedelta  
import datetime as dt
from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
from .Amazon_Target_Performance_PartASIN_NewProduct import amazon_target_performance_partASIN_newproduct
class amazon_target_performance_partASIN:
    def __init__(self) -> None:
        pass

    # 获取上周的一周日期列表
    def get_dates_last_week(self, str_date : str) -> list:
        today = datetime.strptime(str_date, "%Y-%m-%d")
        weekday_today = today.weekday()
        last_sunday = today - timedelta(days=weekday_today + 1)
        dates = []
        for i in range(7):
            date = last_sunday + timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))

        return dates

    # 获取日期列表
    def divide_date_ranges(self) -> list:
        start_date = datetime.strptime("2024-09-01", "%Y-%m-%d")
        current_date = datetime.now()
        date_ranges = []
        while start_date <= current_date:
            end_date = start_date + timedelta(days=30)
            if end_date > current_date:
                end_date = current_date
            date_ranges.append((start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            start_date = end_date + timedelta(days=1)

        return date_ranges
    
    # 判断日期是否在区间
    def is_date_in_range(self, date_str : str, range_str : str) -> bool:  
        # 将日期字符串转换为datetime.date对象  
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()  
        
        # 拆分日期区间字符串  
        start_str, end_str = range_str.split('~')  
        
        # 将起始日期和结束日期字符串转换为datetime.date对象  
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()  
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()  
        
        # 判断目标日期是否在区间内（包括起始日期和结束日期）  
        return start_date <= target_date <= end_date  

    def datetime_dict_h(self) -> dict:
        # 定义起始日期  
        start_key_date = dt.date(2023, 9, 3)  
        start_value_date = dt.date(2024, 9, 1)  
        
        # 定义要生成的周期数  
        num_periods = 53  # 你可以根据需要调整这个数值  
        
        # 初始化数据字典  
        data_dict = {}  
        
        # 生成数据字典  
        for i in range(num_periods):  
            # 计算键的日期范围  
            key_start_date = start_key_date + timedelta(days=i*7)  
            key_end_date = key_start_date + timedelta(days=6)  # 加6天得到结束日期  
            key = f"{key_start_date}~{key_end_date}"  
            
            # 计算值的日期范围  
            value_start_date = start_value_date + timedelta(days=i*7)  
            value_end_date = value_start_date + timedelta(days=6)  # 加6天得到结束日期  
            value = f"{value_start_date}~{value_end_date}" 
            
            # 将键值对添加到字典中  
            data_dict[key] = value  
        return data_dict

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

    def FEISHU_LIRUN_DICT(self, lxzq:str, lxzq_1:str) -> None:
        page_token = ''
        has_more = True
        feishu_datas = []
        while has_more:
            filter_condition = {
                "field_names": [
                    "父ASIN",
                    "国家",
                    "数据状态"
                ],
                "filter": {
                    "conjunction": "or",
                    "conditions": [
                    {
                        "field_name": "领星周期",
                        "operator": "is",
                        "value": [
                        lxzq
                        ]
                    },
                    {
                        "field_name": "领星周期",
                        "operator": "is",
                        "value": [
                        lxzq_1
                        ]
                    }
                    ]
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = 'XHPsbDoxhasv4fswQ9hckwLmnbc', table_id = 'tbl5RlIhqMzC8KkC', filter_condition=filter_condition, page_token = page_token, page_size=500)
            if response['code'] == 0:
                has_more = response['data']['has_more']
                if has_more == False:
                    feishu_datas.extend(response['data']['items'])
                    break
                page_token = response['data']['page_token']
                feishu_datas.extend(response['data']['items'])
            else:
                raise Exception(response['msg'])
        result_dict_newupdate = {}
        result_dict_original = {}
        fasin_yc_list = []
        for feishu_data in feishu_datas:
            if "数据状态" not in feishu_data["fields"]:
                if "父ASIN" in feishu_data["fields"]:
                    result_dict_original.update({feishu_data["fields"]["父ASIN"][0]["text"]+","+feishu_data["fields"]["国家"][0]["text"]:feishu_data["record_id"]})
                else:
                    fasin_yc_list.append(feishu_data["record_id"])
            elif feishu_data["fields"]["数据状态"] != "父ASIN新增":
                if "父ASIN" in feishu_data["fields"]:
                    result_dict_original.update({feishu_data["fields"]["父ASIN"][0]["text"]+","+feishu_data["fields"]["国家"][0]["text"]:feishu_data["record_id"]})
                else:
                    fasin_yc_list.append(feishu_data["record_id"])
            else:
                result_dict_newupdate.update({feishu_data["fields"]["父ASIN"][0]["text"]+","+feishu_data["fields"]["国家"][0]["text"]:feishu_data["record_id"]})
        return [result_dict_original,result_dict_newupdate,fasin_yc_list]

    def main(self):
        # 获取日期映射字典
        datetime_dict = self.datetime_dict_h()
        date_str = datetime.now().strftime("%Y-%m-%d")
        # 获取当天位于当周的的起始日期
        Lx_datetime_weeks = self.get_dates_since_last_sunday(str_date = date_str)
        start_yesterday_str = Lx_datetime_weeks[0].strftime('%Y-%m-%d')
        start_yesterday_end = Lx_datetime_weeks[-1].strftime('%Y-%m-%d')
        dates_last_week = self.get_dates_last_week(str_date = date_str)
        # 获取飞书对应的领星周期
        for _data_key, _data_value in datetime_dict.items():
            if self.is_date_in_range(date_str=start_yesterday_end, range_str=datetime_dict[_data_key]):
                lxzq = _data_key
                break
            else:
                lxzq = ""
        # 获取利润报表数据
        datasstatementprofit = lingxingapi().__StatementProfitParentASIN__(startDate=start_yesterday_str, endDate=start_yesterday_end)
        datasproductperformance = lingxingapi().__ProductPerformance__(start_date=start_yesterday_str, end_date=start_yesterday_end)
        LingxingProfitResult = {}
        Lingxingproductperformance = {}
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

            if type(_data["storeName"]) == list:
                storeName = ""
                for _data_1 in _data["storeName"]:
                    storeName = storeName + _data_1  + ","
                storeName = storeName[:-1]
            else:
                storeName = _data["storeName"]

            if type(_data["localName"]) == list:
                localName = ""
                for _data_1 in _data["localName"]:
                    localName = localName + _data_1  + ","
                localName = localName[:-1]
            else:
                localName = _data["localName"]

            if type(_data["itemName"]) == list:
                itemName = ""
                for _data_1 in _data["itemName"]:
                    itemName = itemName + _data_1  + ","
                itemName = itemName[:-1]
            else:
                itemName = _data["itemName"]

            if type(_data["principalRealname"]) == list:
                principalRealname = ""
                for _data_1 in _data["principalRealname"]:
                    principalRealname = principalRealname + _data_1  + ","
                principalRealname = principalRealname[:-1]
            else:
                principalRealname = _data["principalRealname"]
            LingxingProfitResult.update({
                _data["parentAsin"] + "," + country:{
                    "totalSalesQuantity":_data["totalSalesQuantity"], # 销量
                    "totalSalesAmount":_data["totalSalesAmount"],
                    "SR":_data["totalSalesAmount"] + _data["shippingCredits"] + _data["promotionalRebates"] + _data["fbaInventoryCredit"] + _data["otherInAmount"] + _data["totalSalesRefunds"] + _data["totalFeeRefunds"],# 收入  销售额 + 买家运费 + 促销折扣 + FBA库存赔偿 + 其他收入 + 收入退款额 + 费用退款额
                    "grossProfit":_data["grossProfit"], # 毛利润
                    "localSku":str(_data["localSku"]),
                    "localName":localName,# 品名
                    "storeName":storeName, # 店铺
                    "asin":_data["asin"], # 子Asin
                    "itemName":itemName, # 标题
                    "principalRealname":principalRealname # Listing负责人
                }
            })
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
        # 获取飞书对应的领星周期中的所有记录ID，{父ASIN,国家:ID，....}
        FEISHU_LIRUN_DICT_LIST = self.FEISHU_LIRUN_DICT(lxzq=lxzq,lxzq_1=dates_last_week[0]+"~"+dates_last_week[-1])

        datetime_record_id_original = FEISHU_LIRUN_DICT_LIST[0]
        datetime_record_id_original.update(FEISHU_LIRUN_DICT_LIST[1])
        datetime_record_id_newupdate = FEISHU_LIRUN_DICT_LIST[1]

        payload_list = []
        newupdate_list = []
        exec_dict = {}
        for _data in datetime_record_id_original:
            fields_dict = {}
            record_id = datetime_record_id_original[_data]
            if _data in datetime_record_id_newupdate:
                data_status = "父ASIN新增"
            else:
                data_status = "取数完整"
            try:
                fields_dict.update({
                    "收入实际达成":LingxingProfitResult[_data]["SR"], 
                    "毛利润实际达成":LingxingProfitResult[_data]["grossProfit"], 
                    "销量实际达成":LingxingProfitResult[_data]["totalSalesQuantity"], 
                    "数据状态":data_status
                    })
                # 增加一个列表，检索匹配成功的加入列表，最终删掉这部分检索成功的，留下新增的
                newupdate_list.append(_data)
            except:
                fields_dict.update({
                "收入实际达成":0, 
                "毛利润实际达成":0,
                "销量实际达成":0, 
                })
                # 增加一个列表（加入上年存在，本年当期不存在），先去检索一遍9-1到目前是否存在，存在则为链接已删除，不存在则当期异常
                exec_dict[_data] = record_id
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
            payload_list.append({"record_id": record_id, "fields": fields_dict})
        for _data in FEISHU_LIRUN_DICT_LIST[2]:
            payload_list.append({"record_id": _data, "fields": {
                "大类排名(实现)":0,
                "小类排名(实现)":0,
                "CVR(实现)":0, 
                "CPA(实现)":0, 
                "ACOS(实现)":0,
                "TACOS(实现)":0,
                "广告订单量":0,
                "自然订单量":0,
                "销量实际达成":0,
                "收入实际达成":0,
                "毛利润实际达成":0,
                "数据状态":"父ASIN空值"
                }})
        # 以500为划分，更新回飞书表格，正常的更新
        for _data in [payload_list[i:i + 500] for i in range(0, len(payload_list), 500)]:
            payload_dict = {"records":_data}
            # 上传数据
            while True:
                try:
                    response = feishuapi().__postUpdatesDatas__(app_token = 'XHPsbDoxhasv4fswQ9hckwLmnbc', table_id = 'tbl5RlIhqMzC8KkC', payload_dict = payload_dict)
                    print(response)
                    break
                except:
                    continue
        # 编写新增的录入多维表格
        for _data in newupdate_list:
            try:
                del LingxingProfitResult[_data]
            except:
                continue

        payload_list = []
        for _data in LingxingProfitResult:
            fields = {
                    # "领星周期":lxzq,
                    "领星周期":dates_last_week[0]+"~"+dates_last_week[-1],
                    "父ASIN":str(_data).split(",")[0],
                    "子ASIN":LingxingProfitResult[_data]["asin"],
                    "店铺":LingxingProfitResult[_data]["storeName"],
                    "国家":str(_data).split(",")[1],
                    "品名":LingxingProfitResult[_data]["localName"],
                    "SKU":LingxingProfitResult[_data]["localSku"],
                    "标题":LingxingProfitResult[_data]["itemName"],
                    "Listing负责人":LingxingProfitResult[_data]["principalRealname"],
                    "销量实际达成":LingxingProfitResult[_data]["totalSalesQuantity"],
                    "收入实际达成":LingxingProfitResult[_data]["SR"],
                    "毛利润实际达成":LingxingProfitResult[_data]["grossProfit"],
                    "数据状态":"父ASIN新增"
                }
            try:
                fields.update({
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
                fields.update({
                    "大类排名(实现)":0,
                    "小类排名(实现)":0,
                    "CVR(实现)":0, 
                    "CPA(实现)":0, 
                    "ACOS(实现)":0,
                    "TACOS(实现)":0,
                    "广告订单量":0,
                    "自然订单量":0,
                })
            payload_list.append({"fields": fields})
        # 以500为划分，更新回飞书表格，正常的更新
        for _data in [payload_list[i:i + 500] for i in range(0, len(payload_list), 500)]:
            payload_dict = {"records":_data}
            # 上传数据
            while True:
                try:
                    response = feishuapi().__insertBitableDatas__(app_token="XHPsbDoxhasv4fswQ9hckwLmnbc", table_id="tbl5RlIhqMzC8KkC", payload_dict=payload_dict)
                    print(response)
                    break
                except:
                    continue
        # 编写当期不存在的数据去领星检索本年是否存在
        yc_data_list = []
        for _data_1 in set(exec_dict.keys()):
            yc_data_list.append({"record_id": exec_dict[_data_1], "fields": {
                "数据状态":"上期有本期无"
                }})
        # 以500为划分，更新回飞书表格，正常的更新
        for _data in [yc_data_list[i:i + 500] for i in range(0, len(yc_data_list), 500)]:
            payload_dict = {"records":_data}
            # 上传数据
            while True:
                try:
                    response = feishuapi().__postUpdatesDatas__(app_token = 'XHPsbDoxhasv4fswQ9hckwLmnbc', table_id = 'tbl5RlIhqMzC8KkC', payload_dict = payload_dict)
                    print(response)
                    break
                except:
                    continue
        amazon_target_performance_partASIN_newproduct().main()