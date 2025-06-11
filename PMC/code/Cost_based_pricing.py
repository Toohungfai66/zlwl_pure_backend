from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta  
import json
import requests
import time

class cost_based_pricing:

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

    def FEISHU_FBA_DICT(self,app_token,table_id,project) -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        if project == "mi":
            fields_names = ["SKU"]
        elif project == "hl":
            fields_names = ["币种"]
        elif project == "lr":
            fields_names = ["MSKU"]
        else:
            fields_names = []
        while has_more:
            filter_condition = {
                "field_names": fields_names,
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
        record_id_list = []
        if project == "mi":
            for feishu_data in feishu_datas:
                if "SKU" in feishu_data["fields"]:
                    if feishu_data["fields"]["SKU"][0]["text"] in result_dict:
                        values_1 = result_dict[feishu_data["fields"]["SKU"][0]["text"]] + "," + feishu_data["record_id"]
                        result_dict.update({feishu_data["fields"]["SKU"][0]["text"]:values_1})
                    else:
                        result_dict.update({feishu_data["fields"]["SKU"][0]["text"]:feishu_data["record_id"]})
                else:
                    record_id_list.append(feishu_data["record_id"])
            result_dict.update({"None":record_id_list})
        elif project == "hl":
            for feishu_data in feishu_datas:
                result_dict.update({feishu_data["record_id"]:feishu_data["fields"]["币种"][0]["text"]})
        elif project == "lr":
            for feishu_data in feishu_datas:
                result_dict.update({feishu_data["record_id"]:feishu_data["fields"]["MSKU"][0]["text"]})
        else:
            pass
        return result_dict
    
    def currencymonth(self):
        currencyMonth = lingxingapi().__currencyMonth__()
        insert_data_list = []
        for _data in currencyMonth:
            fields = {
                "币种":_data["code"],
                "官方汇率":float(_data["rate_org"]),
                "我的汇率":float(_data["my_rate"])
            }
            insert_data_list.append({"fields": fields})

        delete_data_list = list(self.FEISHU_FBA_DICT(app_token = 'XjL9biLNPaja1Tsb0vRcGGSFnLg', table_id = 'tblRLPODgo4lm6db', project="hl").keys())
        for _data in [delete_data_list[i:i + 500] for i in range(0, len(delete_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__deleteBitableDatas__(app_token = 'XjL9biLNPaja1Tsb0vRcGGSFnLg', table_id = 'tblRLPODgo4lm6db', payload_dict = payload_dict)

        for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
            payload_dict = {"records":_data}
            print(feishuapi().__insertBitableDatas__(app_token = 'XjL9biLNPaja1Tsb0vRcGGSFnLg', table_id = 'tblRLPODgo4lm6db', payload_dict = payload_dict))

    def get_months_this_year(self):
        # 获取当前年份和月份
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # 生成从今年1月到当前月份的所有月份字符串
        months = []
        for month in range(1, current_month + 1):
            # 格式化月份为两位数字
            month_str = f"{month:02d}"
            months.append(f"{current_year}-{month_str}")
        
        return months
    
    def main(self):
        self.currencymonth()
        productlist = lingxingapi().__ProductList__()
        productIds = []
        for _data in productlist:
            productIds.append(str(_data["id"]))
        all_data = []
        for _data in [productIds[i:i + 100] for i in range(0, len(productIds), 100)]:
            all_data.extend(lingxingapi().__ProductDetailed__(productIds=_data))
        FeishuResult = self.FEISHU_FBA_DICT(app_token = 'XjL9biLNPaja1Tsb0vRcGGSFnLg', table_id = 'tbl336biNGE4zRbG', project="mi")
        update_data_list = []
        pd_list = ["None"]
        for _data in all_data:
            if _data["sku"] in FeishuResult:
                for _data_1 in str(FeishuResult[_data["sku"]]).split(","):
                    fields = {
                        "单位":_data["unit"],
                        "长(商品)":float(_data["cg_product_length"]),
                        "宽(商品)":float(_data["cg_product_width"]),
                        "高(商品)":float(_data["cg_product_height"]),
                        "长(外箱)":float(_data["cg_box_length"]),
                        "宽(外箱)":float(_data["cg_box_width"]),
                        "高(外箱)":float(_data["cg_box_height"]),
                        "单箱数量":int(_data["cg_box_pcs"]),
                        "实重(外箱)":float(_data["cg_box_weight"])
                        }
                    update_data_list.append({
                        "record_id":_data_1,
                        "fields":fields
                    })
                    pd_list.append(_data["sku"])
        None_list = FeishuResult["None"]
        for _data in list(set(FeishuResult.keys()) - set(pd_list)):
            None_list = None_list + str(FeishuResult[_data]).split(",")
        for _data in None_list:
            fields = {
                "单位":"SKU为空或产品管理未找到对应SKU",
                "长(商品)":0,
                "宽(商品)":0,
                "高(商品)":0,
                "长(外箱)":0,
                "宽(外箱)":0,
                "高(外箱)":0,
                "单箱数量":0,
                "实重(外箱)":0
                }
            update_data_list.append({
                "record_id":_data,
                "fields":fields
            })
        if len(update_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data}
                print(feishuapi().__postUpdatesDatas__(app_token = 'XjL9biLNPaja1Tsb0vRcGGSFnLg', table_id = 'tbl336biNGE4zRbG', payload_dict = payload_dict))

        update_data_list = []
        FeishuResult_1 = self.FEISHU_FBA_DICT(app_token = 'XjL9biLNPaja1Tsb0vRcGGSFnLg', table_id = 'tbl336biNGE4zRbG', project="lr")
        response_dict = {}
        months = self.get_months_this_year()
        for month in months:
            ProfitStatement = lingxingapi().__ProfitStatement__(startDate=month,endDate=month)
            for _data in ProfitStatement:
                if _data["msku"] in response_dict:
                    response_dict.update({_data["msku"]:{"采购成本":_data["cgPriceTotal"] + response_dict[_data["msku"]]["采购成本"],"头程成本":_data["cgTransportCostsTotal"] + response_dict[_data["msku"]]["头程成本"]}})
                else:
                    response_dict.update({_data["msku"]:{"采购成本":_data["cgPriceTotal"],"头程成本":_data["cgTransportCostsTotal"]}})

        for _data in FeishuResult_1:
            if FeishuResult_1[_data] in response_dict:
                fields = {"销售成本总额":abs(response_dict[FeishuResult_1[_data]]["采购成本"]+response_dict[FeishuResult_1[_data]]["头程成本"])}
            else:
                fields = {"销售成本总额":0}
            update_data_list.append({
                "record_id":_data,
                "fields":fields
            })
        if len(update_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data}
                print(feishuapi().__postUpdatesDatas__(app_token = 'XjL9biLNPaja1Tsb0vRcGGSFnLg', table_id = 'tbl336biNGE4zRbG', payload_dict = payload_dict))