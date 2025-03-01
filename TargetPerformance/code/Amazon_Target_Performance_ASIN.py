import requests
import json
from urllib.parse import unquote
from datetime import datetime, timedelta  
import datetime as dt
from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi

class amazon_target_performance_asin:
    def __init__(self) -> None:
        pass

    def get_dates_last_week(self, str_date) -> list:
        today = datetime.strptime(str_date, "%Y-%m-%d")
        # 计算本周的周几（0表示周一，6表示周日）
        weekday_today = today.weekday()
        # 找到上周日的日期
        last_sunday = today - timedelta(days=weekday_today + 1)
        dates = []
        for i in range(7):
            date = last_sunday + timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))

        return dates

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

    def is_date_in_range(self, date_str, range_str) -> bool:  
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


    def get_dates_since_last_sunday(self, str_date) -> list:  
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

    def FEISHU_LIRUN_DICT(self, lxzq,app_token,table_id) -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        while has_more:
            filter_condition = {
                "field_names": [
                    "子ASIN",
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
            response = self.get_bitable_datas(app_token = app_token, table_id = table_id, filter_condition=filter_condition, page_token = page_token, page_size=500)
            if response['code'] == 0:
                has_more = response['data']['has_more']
                if has_more == False:
                    feishu_datas.extend(response['data']['items'])
                    break
                page_token = response['data']['page_token']
                feishu_datas.extend(response['data']['items'])
            else:
                raise Exception(response['msg'])

        result_dict_original = {}
        for feishu_data in feishu_datas:
            try:
                result_dict_original.update({feishu_data["fields"]["子ASIN"][0]["text"]+"|"+feishu_data["fields"]["国家"][0]["text"]:feishu_data["record_id"]})
            except:
                continue
        return result_dict_original

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
        app_token = "NnQYbJpdBaOuGbsjBcLcy9YinWc"
        if lxzq in [list(self.datetime_dict_h().keys())[_data] for _data in range(list(self.datetime_dict_h().keys()).index('2023-09-03~2023-09-09'),list(self.datetime_dict_h().keys()).index('2023-11-26~2023-12-02')+1)]:
            table_id = "tblDyGw0fDVkYlOi"
            Xz_table_id = "tblEo4l7S01jITsi"
        elif lxzq in [list(self.datetime_dict_h().keys())[_data] for _data in range(list(self.datetime_dict_h().keys()).index('2023-12-03~2023-12-09'),list(self.datetime_dict_h().keys()).index('2024-02-25~2024-03-02')+1)]:
            table_id = "tbluZ7bMAypcEGFN"
            Xz_table_id = "tblFQUtKMxZtB5Os"
        elif lxzq in [list(self.datetime_dict_h().keys())[_data] for _data in range(list(self.datetime_dict_h().keys()).index('2024-03-03~2024-03-09'),list(self.datetime_dict_h().keys()).index('2024-05-26~2024-06-01')+1)]:
            table_id = "tblvlabUE8UvItob"
            Xz_table_id = "tbl2VsWK7BASlyc5"
        else:
            table_id = "tblEJVNFlu0qH9ly"
            Xz_table_id = "tblZ1p76CgLW1Spj"
        # 获取利润报表数据,产品表现数据
        datasstatementprofit = lingxingapi().__StatementProfit__(startDate=start_yesterday_str, endDate=start_yesterday_end)
        datasproductperformance = lingxingapi().__ProductPerformance__(start_date=start_yesterday_str, end_date=start_yesterday_end)
        # 处理报表数据
        LingxingProfitResult = {}
        for _data in datasstatementprofit:
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
                _data["asin"] + "|" + country:{
                    "totalSalesQuantity":_data["totalSalesQuantity"], # 销量
                    "totalSalesAmount":_data["totalSalesAmount"], # 销售额
                    "SR":_data["totalSalesAmount"] + _data["shippingCredits"] + _data["promotionalRebates"] + _data["fbaInventoryCredit"] + _data["otherInAmount"] + _data["totalSalesRefunds"] + _data["totalFeeRefunds"],# 收入  销售额 + 买家运费 + 促销折扣 + FBA库存赔偿 + 其他收入 + 收入退款额 + 费用退款额
                    "grossProfit":_data["grossProfit"], # 毛利润
                    "localSku":str(_data["localSku"]), # SKU
                    "localName":localName,# 品名
                    "storeName":storeName, # 店铺
                    "parentAsin":_data["parentAsin"], # 父Asin
                    "itemName":itemName, # 标题
                    "principalRealname":principalRealname,  # Listing负责人
                    "brandName":_data["brandName"], # 品牌
                    "totalReshipQuantity":_data["totalReshipQuantity"], # 补换货量
                    "mcFbaFulfillmentFeesQuantity":_data["mcFbaFulfillmentFeesQuantity"], # 多渠道销量
                    "totalAdsSales":_data["totalAdsSales"], # 广告销售额
                    "totalAdsSalesQuantity":_data["totalAdsSalesQuantity"], # 广告销量
                    "shippingCredits":_data["shippingCredits"], # 买家运费
                    "promotionalRebates":_data["promotionalRebates"], # 促销折扣
                    "fbaInventoryCredit":_data["fbaInventoryCredit"], # FBA库存赔偿
                    "cashOnDelivery":_data["cashOnDelivery"], # COD
                    "otherInAmount":_data["otherInAmount"], # 其他收入
                    "totalSalesRefunds":_data["totalSalesRefunds"], # 收入退款额
                    "totalFeeRefunds":_data["totalFeeRefunds"], # 费用退款额
                    "refundsQuantity":_data["refundsQuantity"], # 退款量
                    "refundsRate":_data["refundsRate"], # 退款率
                    "fbaReturnsQuantity":_data["fbaReturnsQuantity"], # 退货量	
                    "platformFee":_data["platformFee"], # 平台费用
                    "fbaDeliveryFee":_data["fbaDeliveryFee"], # FBA发货费
                    "otherTransactionFees":_data["otherTransactionFees"], # 其他订单费用
                    "totalAdsCost":_data["totalAdsCost"], # 广告费
                    "promotionFee":_data["promotionFee"], # 推广费
                    "totalStorageFee":_data["totalStorageFee"], # FBA仓储费
                    "sharedFbaIntegerernationalInboundFee":_data["sharedFbaIntegerernationalInboundFee"], # FBA国际物流货运费
                    "adjustments":_data["adjustments"], # 调整费用
                    "totalPlatformOtherFee":_data["totalPlatformOtherFee"], # 平台其他费
                    "customOrderFeePrincipal":_data["customOrderFeePrincipal"], # 站外推广费-本金
                    "customOrderFeeCommission":_data["customOrderFeeCommission"], # 站外推广费-佣金
                    "totalSalesTax":_data["totalSalesTax"], # 销售税
                    "salesTaxRefund":_data["salesTaxRefund"], # 销售税退款额
                    "tdsSection194ONet":_data["tdsSection194ONet"], # 混合网络费
                    "cgPriceTotal":_data["cgPriceTotal"], # 采购成本
                    "cgUnitPrice":_data["cgUnitPrice"], # 采购均价
                    "proportionOfCg":_data["proportionOfCg"], # 采购占比
                    "cgTransportCostsTotal":_data["cgTransportCostsTotal"], # 头程成本
                    "cgTransportUnitCosts":_data["cgTransportUnitCosts"], # 头程均价
                    "proportionOfCgTransport":_data["proportionOfCgTransport"], # 头程占比
                    "cgOtherCostsTotal":_data["cgOtherCostsTotal"], # 其他成本
                    "cgOtherUnitCosts":_data["cgOtherUnitCosts"], # 其他均价
                    "proportionOfCgOtherCosts":_data["proportionOfCgOtherCosts"], # 其他占比
                    "totalCost":_data["totalCost"], # 合计成本
                    "proportionOfTotalCost":_data["proportionOfTotalCost"], # 合计成本占比
                    "grossRate":_data["grossRate"], # 毛利率
                    "cgOtherUnitCosts":_data["cgOtherUnitCosts"], # 其他均价
                    "adsSdCost":_data["adsSdCost"], # 推广费（SD费用）
                }
            })
        # 处理表现数据
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
                    _data["asins"][0]["asin"] + "|" + _data["seller_store_countries"][0]["country"]:{
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
            if _data["asins"][0]["asin"] + "|" + _data["seller_store_countries"][0]["country"] not in Lingxingproductperformance:
                Lingxingproductperformance.update(Lingxingproductdict)
            elif Lingxingproductperformance[_data["asins"][0]["asin"] + "|" + _data["seller_store_countries"][0]["country"]]["cate_rank"] < _data["cate_rank"]:
                Lingxingproductperformance.update(Lingxingproductdict)
            else:
                continue

        # 获取飞书对应的领星周期中的所有记录ID，{子ASIN,国家:ID，....}yp
        feishu_original = self.FEISHU_LIRUN_DICT(lxzq=lxzq, app_token=app_token,table_id=table_id)
        feishu_newupdate = self.FEISHU_LIRUN_DICT(lxzq=dates_last_week[0] + "~" + dates_last_week[-1], app_token=app_token,table_id=Xz_table_id)

        payload_original = []
        insert_newdatas = []
        new_payload_original = []
        for _data in LingxingProfitResult:
            fields_dict = {}
            # 基础数据增加
            fields_dict.update({
                "收入实际达成":LingxingProfitResult[_data]["SR"], 
                "毛利润实际达成":LingxingProfitResult[_data]["grossProfit"], 
                "销量实际达成":LingxingProfitResult[_data]["totalSalesQuantity"], 
                })
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
            if _data in feishu_original:
                payload_original.append({"record_id": feishu_original[_data], "fields": fields_dict})
            else:
                fields_dict.update({
                    "领星周期":dates_last_week[0] + "~" + dates_last_week[-1],
                    "子ASIN":str(_data).split("|")[0],
                    "国家":str(_data).split("|")[1],
                    "销量":LingxingProfitResult[_data]["totalSalesQuantity"], # 销量
                    "销售额":LingxingProfitResult[_data]["totalSalesAmount"], # 销售额
                    "领星毛利润":LingxingProfitResult[_data]["grossProfit"], # 毛利润
                    "SKU":LingxingProfitResult[_data]["localSku"], # SKU
                    "品名":LingxingProfitResult[_data]["localName"],# 品名
                    "店铺":LingxingProfitResult[_data]["storeName"], # 店铺
                    "父ASIN":LingxingProfitResult[_data]["parentAsin"], # 父Asin
                    "标题":LingxingProfitResult[_data]["itemName"], # 标题
                    "Listing负责人":LingxingProfitResult[_data]["principalRealname"],  # Listing负责人
                    "品牌":LingxingProfitResult[_data]["brandName"], # 品牌
                    "补（换）货量":LingxingProfitResult[_data]["totalReshipQuantity"], # 补换货量
                    "多渠道销量":LingxingProfitResult[_data]["mcFbaFulfillmentFeesQuantity"], # 多渠道销量
                    "广告销售额":LingxingProfitResult[_data]["totalAdsSales"], # 广告销售额
                    "广告销量":LingxingProfitResult[_data]["totalAdsSalesQuantity"], # 广告销量
                    "买家运费":LingxingProfitResult[_data]["shippingCredits"], # 买家运费
                    "促销折扣":LingxingProfitResult[_data]["promotionalRebates"], # 促销折扣
                    "FBA库存赔偿":LingxingProfitResult[_data]["fbaInventoryCredit"], # FBA库存赔偿
                    "COD":LingxingProfitResult[_data]["cashOnDelivery"], # COD
                    "其他收入":LingxingProfitResult[_data]["otherInAmount"], # 其他收入
                    "收入退款额":LingxingProfitResult[_data]["totalSalesRefunds"], # 收入退款额
                    "费用退款额":LingxingProfitResult[_data]["totalFeeRefunds"], # 费用退款额
                    "退款量":LingxingProfitResult[_data]["refundsQuantity"], # 退款量
                    "退款率":LingxingProfitResult[_data]["refundsRate"], # 退款率
                    "退货量":LingxingProfitResult[_data]["fbaReturnsQuantity"], # 退货量	
                    "平台费":LingxingProfitResult[_data]["platformFee"], # 平台费用
                    "FBA发货费":LingxingProfitResult[_data]["fbaDeliveryFee"], # FBA发货费
                    "其他订单费用":LingxingProfitResult[_data]["otherTransactionFees"], # 其他订单费用
                    "广告费":LingxingProfitResult[_data]["totalAdsCost"], # 广告费
                    "推广费":LingxingProfitResult[_data]["promotionFee"], # 推广费
                    "FBA仓储费":LingxingProfitResult[_data]["totalStorageFee"], # FBA仓储费
                    "FBA国际物流货运费":LingxingProfitResult[_data]["sharedFbaIntegerernationalInboundFee"], # FBA国际物流货运费
                    "调整费用":LingxingProfitResult[_data]["adjustments"], # 调整费用
                    "平台其他费":LingxingProfitResult[_data]["totalPlatformOtherFee"], # 平台其他费
                    "站外推广费-本金":LingxingProfitResult[_data]["customOrderFeePrincipal"], # 站外推广费-本金
                    "站外推广费-佣金":LingxingProfitResult[_data]["customOrderFeeCommission"], # 站外推广费-佣金
                    "销售税":LingxingProfitResult[_data]["totalSalesTax"], # 销售税
                    "销售税退款额":LingxingProfitResult[_data]["salesTaxRefund"], # 销售税退款额
                    "混合网络费":LingxingProfitResult[_data]["tdsSection194ONet"], # 混合网络费
                    "采购成本":LingxingProfitResult[_data]["cgPriceTotal"], # 采购成本
                    "采购均价":LingxingProfitResult[_data]["cgUnitPrice"], # 采购均价
                    "采购占比":LingxingProfitResult[_data]["proportionOfCg"], # 采购占比
                    "头程成本":LingxingProfitResult[_data]["cgTransportCostsTotal"], # 头程成本
                    "头程均价":LingxingProfitResult[_data]["cgTransportUnitCosts"], # 头程均价
                    "头程占比":LingxingProfitResult[_data]["proportionOfCgTransport"], # 头程占比
                    "其他成本":LingxingProfitResult[_data]["cgOtherCostsTotal"], # 其他成本
                    "其他均价":LingxingProfitResult[_data]["cgOtherUnitCosts"], # 其他均价
                    "其他占比":LingxingProfitResult[_data]["proportionOfCgOtherCosts"], # 其他占比
                    "合计成本":LingxingProfitResult[_data]["totalCost"], # 合计成本
                    "合计成本占比":LingxingProfitResult[_data]["proportionOfTotalCost"], # 合计成本占比
                    "毛利率":LingxingProfitResult[_data]["grossRate"], # 毛利率
                    "其他均价":LingxingProfitResult[_data]["cgOtherUnitCosts"], # 其他均价
                    "推广费（SD费用）":LingxingProfitResult[_data]["adsSdCost"], # 推广费（SD费用）
                })
                if _data in new_payload_original:
                    new_payload_original.append({"record_id": feishu_newupdate[_data], "fields": fields_dict})
                else:
                    insert_newdatas.append({"fields": fields_dict})
        # 原表更新
        if len(payload_original) != 0:
            for _data in [payload_original[i:i + 500] for i in range(0, len(payload_original), 500)]:
                payload_dict = {"records":_data}
                response = feishuapi().__postUpdatesDatas__(app_token = app_token, table_id = table_id, payload_dict = payload_dict)
                print(response)
        # 新增表更新
        if len(new_payload_original) != 0:
            for _data in [new_payload_original[i:i + 500] for i in range(0, len(new_payload_original), 500)]:
                payload_dict = {"records":_data}
                response = feishuapi().__postUpdatesDatas__(app_token = app_token, table_id = Xz_table_id, payload_dict = payload_dict)
                print(response)
        # 新增表插入
        if len(insert_newdatas) != 0:
            for _data in [insert_newdatas[i:i + 500] for i in range(0, len(insert_newdatas), 500)]:
                payload_dict = {"records":_data}
                response = feishuapi().__insertBitableDatas__(app_token = app_token, table_id = Xz_table_id, payload_dict = payload_dict)
                print(response)