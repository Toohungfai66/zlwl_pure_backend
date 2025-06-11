import requests

class lingxingrpa:

    def __init__(self, cookies : str) -> None:
        self.x_ak_company_id = "901114485580800512"
        self.cookies = cookies
    
    def __getBDKCdata__(self, wid_list) -> dict:
        url = "https://erp.lingxing.com/api/storage/lists"
        headers = {
            "x-ak-company-id":self.x_ak_company_id,
            'Auth-Token':self.cookies,
        }
        offset = 0
        result_dict = {}
        key_num = 0
        while True:
            datas = {
                "wid_list":wid_list,
                "mid_list":"",
                "sid_list":"",
                "cid_list":"",
                "bid_list":"",
                "principal_list":"",
                "product_type_list":"",
                "product_attribute":"",
                "product_status":"",
                "search_field":"fnsku",
                "search_value":"",
                "is_sku_merge_show":0,
                "is_hide_zero_stock":1,
                "offset":offset,
                "length":200,
                "sort_field":"",
                "sort_type":"",
                "gtag_ids":"",
                "senior_search_list":"[]",
                "permission_uid_list":"",
                "country_code_list":"",
                "req_time_sequence":"/api/storage/lists$$2"
                }
            response = requests.post(url=url,json=datas,headers=headers).json()
            if len(response["data"]["list"]) == 0:
                break
            for data in response["data"]["list"]:
                key_num += 1
                try:
                    purchase_price = float(data["purchase_price"])
                except:
                    purchase_price = 0
                try:
                    stock_cost = float(data["stock_cost"])
                except:
                    stock_cost = 0
                if len(data["msku_list"]) == 0:
                    msku = ""
                else:
                    msku = data["msku_list"][0]
                if len(data["country_name_list"]) == 0:
                    country = ""
                else:
                    country = data["country_name_list"][0]
                if len(data["store_name_list"]) == 0:
                    store = ""
                else:
                    store = data["store_name_list"][0]
                result_dict[key_num] = {
                    "product_name":str(data["product_name"]).split("&")[0],
                    "wh_name":data["wh_name"],
                    "yj_one":int(data["section1"]),
                    "yj_two":int(data["section2"]),
                    "gy":int(data["total"])-int(data["section1"])-int(data["section2"]),
                    "fnsku":data["fnsku"],
                    "sku":data["sku"],
                    "msku":msku,
                    "purchase_price":purchase_price,
                    "stock_cost":stock_cost,
                    "store_name_list":store,
                    "spu":data["spu"],
                    "spu_name":data["spu_name"],
                    "category_name":data["category_name"],
                    "country":country,
                    "brand_name":data["brand_name"],
                    "principal_name_list":data["principal_name_list"],
                    "good_num":data["good_num"]
                    }
            offset += 200
        return result_dict
    
    def __getListing__(self) -> dict:
        url = "https://gw.lingxingerp.com/listing-api/api/product/showOnline"
        headers = {
            "x-ak-company-id":self.x_ak_company_id,
            'Auth-Token':self.cookies,
        }
        offset = 0
        result_response = []
        while True:
            datas = {
                "offset":offset,
                "length":200,
                "search_field":"",
                "pvi_ids":"",
                "exact_search":0,
                "sids":"",
                "status":"1,0",
                "is_pair":"",
                "fulfillment_channel_type":"",
                "global_tag_ids":"",
                "req_time_sequence":"/listing-api/api/product/showOnline$$5"
                }
            response = requests.post(url=url,json=datas,headers=headers).json()
            print(response)
            if len(response["data"]["list"]) == 0:
                break
            result_response.extend(response["data"]["list"])
            offset += 200
        return result_response
    
    def __getFBAKCdata__(self) -> dict:
        url = "https://erp.lingxing.com/api/storage/fbaLists"
        headers = {
            "x-ak-company-id":self.x_ak_company_id,
            'Auth-Token':self.cookies,
        }
        offset = 0
        result_dict = {}
        dict_key = 0
        while True:
            datas = {
                "cid":"",
                "bid":"",
                "attribute":"",
                "asin_principal":"",
                "search_field":"parent_asin",
                "is_cost_page":0,
                "status":"",
                "senior_search_list":"[]",
                "offset":offset,
                "length":200,
                "fulfillment_channel_type":"",
                "is_hide_zero_stock":"0",
                "is_parant_asin_merge":"0",
                "is_contain_del_ls":"0",
                "req_time_sequence":"/api/storage/fbaLists$$3"
                }
            response = requests.post(url=url,json=datas,headers=headers).json()
            if len(response["list"]) == 0:
                break
            for data in response["list"]:
                dict_key += 1
                # 判断父ASIN是否在字典中
                if "fnsku" in data:
                    fnsku = data["fnsku"]
                else:
                    fnsku = ""
                ls_dict = {
                    "fnsku":fnsku,
                    "name":data["name"],
                    "spu":data["spu"],
                    "spu_name":data["spu_name"],
                    "category_text":data["category_text"],
                    "product_brand_text":data["product_brand_text"],
                    "product_name":data["product_name"],
                    "asin":data["asin"],
                    "sku":data["sku"],
                    "seller_sku":data["seller_sku"],
                    "parent_asin_real":data["parent_asin_real"],
                    "asin_principal":data["asin_principal_list"],
                    "total":data["total"],
                    "total_amount":float(data["total_amount"]),
                    "stock_up_num":data["stock_up_num"],
                    "stock_up_num_price":float(data["stock_up_num_price"]),
                    "afn_inbound_shipped_quantity":data["afn_inbound_shipped_quantity"],
                    "afn_inbound_shipped_quantity_price":float(data["afn_inbound_shipped_quantity_price"]),
                    "available_total":data["available_total"],
                    "available_total_price":float(data["available_total_price"]),
                    "inv_age_0_to_60_days":data["inv_age_0_to_30_days"] + data["inv_age_31_to_60_days"],
                    "inv_age_0_to_60_price":float(data["inv_age_0_to_30_price"]) + float(data["inv_age_31_to_60_price"]),
                    "inv_age_61_to_90_days":data["inv_age_61_to_90_days"],
                    "inv_age_61_to_90_price":float(data["inv_age_61_to_90_price"]),
                    "inv_age_91_to_180_days":data["inv_age_91_to_180_days"],
                    "inv_age_91_to_180_price":float(data["inv_age_91_to_180_price"]),
                    "inv_age_181_plus_days":data["inv_age_181_to_270_days"] + data["inv_age_271_to_365_days"] + data["inv_age_365_plus_days"],
                    "inv_age_181_plus_price":float(data["inv_age_181_to_270_price"]) + float(data["inv_age_271_to_365_price"]) + float(data["inv_age_365_plus_price"]),
                }
                result_dict[dict_key] = ls_dict
            offset += 200
        return result_dict
    
    def __getProductList__(self) -> dict:
        url = "https://erp.lingxing.com/api/product/lists"
        headers = {
            "x-ak-company-id":self.x_ak_company_id,
            'Auth-Token':self.cookies,
        }
        offset = 0
        result_response = []
        while True:
            datas = {
                "search_field_time":"create_time",
                "product_creator_uid":[],
                "product_developer_uid":[],
                "permission_uid":[],
                "cg_opt_uid":[],
                "supplier_id":[],
                "sort_field":"create_time",
                "sort_type":"desc",
                "search_field":"msku",
                "attribute":[],
                "status":[],
                "open_status":"",
                "gtag_ids":"",
                "senior_search_list":"[]",
                "single_product_id":[],
                "is_matched_listing":"",
                "is_matched_alibaba":"",
                "relation_aux":"",
                "is_have_pic":"",
                "cg_package":"",
                "cg_product_gross_weight":{
                    "left":"",
                    "right":"",
                    "symbol":"gt"
                    },
                "cg_price":{
                    "left":"",
                    "right":"",
                    "symbol":"gt"
                    },
                "cg_transport_costs":{
                    "left":"",
                    "right":"",
                    "symbol":"gt",
                    "country_code":"US"
                    },
                "offset":offset,
                "is_combo":"",
                "length":200,
                "is_aux":0,
                "product_type":[1,2],
                "selected_product_ids":"",
                "req_time_sequence":"/api/product/lists$$16"
                }
            response = requests.post(url=url,json=datas,headers=headers).json()
            if len(response["data"]["list"]) == 0:
                break
            result_response.extend(response["data"]["list"])
            offset += 200
        return result_response