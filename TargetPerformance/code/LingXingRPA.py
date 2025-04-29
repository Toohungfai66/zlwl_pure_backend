import requests

class lingxingrpa:

    def __init__(self, cookies : str) -> None:
        self.x_ak_company_id = "901114485580800512"
        self.cookies = cookies

    def __getProfitdata__(self, start : str, end : str, searchValue = []) -> dict:
        url = "https://gw.lingxingerp.com/bd/profit/report/report/parent/asin/list"
        headers = {
            "x-ak-company-id":self.x_ak_company_id,
            'Auth-Token':self.cookies,
        }
        offset = 0
        result_dict = {}
        while True:
            datas = {
                "startDate":start,
                "endDate":end,
                "offset":offset,
                "length":50,
                "mids":[],
                "sids":[],
                "currencyCode":"CNY",
                "cids":[],
                "bids":[],
                "principalUids":[],
                "productDeveloperUids":[],
                "searchField":"parent_asin",
                "searchValue":searchValue,
                "sortField":"totalSalesQuantity",
                "sortType":"desc",
                "isDisplayByDate":"",
                "version":"",
                "listingTagIds":[],
                "isMonthly":"false",
                "req_time_sequence":"/bd/profit/report/report/parent/asin/list$$1"
                }
            
            try:
                response = requests.post(url=url,json=datas,headers=headers).json()
                if len(response["data"]["records"]) == 0:
                    break
                datas = response["data"]["records"]
                for data in datas:
                    if len(data["parentAsin"])==0:
                        continue
                    if type(data["country"]) == list:
                        country = ""
                        for _data in data["country"]:
                            country = country + _data  + ","
                        country = country[:-1]
                    else:
                        country = data["country"]

                    if type(data["storeName"]) == list:
                        storeName = ""
                        for _data in data["storeName"]:
                            storeName = storeName + _data  + ","
                        storeName = storeName[::-1]
                    else:
                        storeName = data["storeName"]

                    if type(data["localName"]) == list:
                        localName = ""
                        for _data in data["localName"]:
                            localName = localName + _data  + ","
                        localName = localName[::-1]
                    else:
                        localName = data["localName"]

                    if type(data["itemName"]) == list:
                        itemName = ""
                        for _data in data["itemName"]:
                            itemName = itemName + _data  + ","
                        itemName = itemName[::-1]
                    else:
                        itemName = data["itemName"]

                    if type(data["principalRealname"]) == list:
                        principalRealname = ""
                        for _data in data["principalRealname"]:
                            principalRealname = principalRealname + _data  + ","
                        principalRealname = principalRealname[::-1]
                    else:
                        principalRealname = data["principalRealname"]
                    result_dict.update({
                        data["parentAsin"] + "," + country:{
                            "totalSalesQuantity":data["totalSalesQuantity"], # 销量
                            "totalSalesAmount":data["totalSalesAmount"],
                            "SR":data["totalSalesAmount"] + data["shippingCredits"] + data["promotionalRebates"] + data["fbaInventoryCredit"] + data["otherInAmount"] + data["totalSalesRefunds"] + data["totalFeeRefunds"],# 收入  销售额 + 买家运费 + 促销折扣 + FBA库存赔偿 + 其他收入 + 收入退款额 + 费用退款额
                            "grossProfit":data["grossProfit"], # 毛利润
                            "localSku":str(data["localSku"]),
                            "localName":localName,# 品名
                            "storeName":storeName, # 店铺
                            "asin":data["asin"], # 子Asin
                            "itemName":itemName, # 标题
                            "principalRealname":principalRealname # Listing负责人
                            }})
            except:
                break
            offset += 50
        return result_dict
    
    def __getWFSKCdata__(self) -> dict:
        url = "https://gw.lingxingerp.com/mp-platform-warehouse-api/api/walmart/walmartStockSearch"
        headers = {
            "x-ak-company-id":self.x_ak_company_id,
            'Auth-Token':self.cookies,
        }
        current = 1
        result_dict = {}
        while True:
            datas = {
                "hideZeroStorage":0,
                "storeIdList":[],
                "warehouseList":[],
                "goodStatusList":[],
                "custom":{
                    "type":1,
                    "likeContent":"",
                    "inContentList":[]
                    },
                "selectTypeEnum":"COUNT_TYPE",
                "current":current,
                "size":200,
                "orderColumnType":"",
                "orderWay":0,
                "req_time_sequence":"/mp-platform-warehouse-api/api/walmart/walmartStockSearch$$6"
                }
            response = requests.post(url=url,json=datas,headers=headers).json()
            if len(response["data"]["page"]["records"]) == 0:
                break
            for data in response["data"]["page"]["records"]:
                if data["purchasePrice"] == None:
                    data["purchasePrice"] = 0
                result_dict[data["msku"]] = {
                    "warehouseName":data["warehouseName"], # 仓库
                    "gtin":data["gtin"],
                    "itemId":int(data["itemId"]), # 商品平台ID
                    "productName":data["productName"], # 品名
                    "platformProductStatus":data["platformProductStatus"], # 商品状态
                    "quantity":int(data["quantity"]), #总库存数量 
                    "quantity_cb":int(data["quantity"]) * float(data["purchasePrice"]),#总库存金额
                    "availableQuantity":int(data["availableQuantity"]), # wfs可售
                    "unabledWarehousingQuantity":int(data["unabledWarehousingQuantity"]), # 无法入库数量
                    "inboundQuantity":int(data["inboundQuantity"]),# 标发在途
                    "inboundQuantity_cb":int(data["inboundQuantity"]) * float(data["purchasePrice"]),# 标发在途金额
                    "last30DaysUnitsReceived":int(data["last30DaysUnitsReceived"]), # 近30天入库
                    "last30DaysPoUnits":int(data["last30DaysPoUnits"]), # 近30天计划入库
                }
            current += 1
        return result_dict