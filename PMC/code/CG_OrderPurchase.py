from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta  
import json
import requests

class cg_orderPurchase:

    def __init__(self):
        pass

    def get_dates_since_last_sunday(self, str_date) -> list:  
        today = datetime.strptime(str_date,"%Y-%m-%d")
        today_weekday = today.weekday()
        last_sunday = today - timedelta(days=today_weekday + 1) if today_weekday != 6 else today
        dates = [(last_sunday + timedelta(days=i)).date().strftime('%Y-%m-%d') for i in range((today - last_sunday).days + 1)]  
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

    def FEISHU_FBA_DICT(self) -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        while has_more:
            filter_condition = {
                "field_names": [
                    "ID",
                ],
                "filter": {
                    "conjunction": "and",
                    "conditions": []
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblsiC3jAdIqbbfG', filter_condition=filter_condition, page_token = page_token, page_size=500)
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
            result_dict.update({feishu_data["fields"]["ID"]:feishu_data["record_id"]})
        return result_dict

    def main(self):
        date_str = datetime.now()
        end_date = date_str.strftime("%Y-%m-%d")
        start_date = date_str - timedelta(days=365)
        start_date = start_date.strftime("%Y-%m-%d")
        # 采购计划领星数据整理
        response_lx_planpurchase = lingxingapi().__getOrderPurchase__(start_date=start_date,end_date=end_date)
        FeishuReult = self.FEISHU_FBA_DICT()
        sid_list = lingxingapi().__AmazonStore__()
        sid_dict = {}
        for _data in sid_list["data"]:
            sid_dict.update({_data["sid"]:_data["name"]})
        sid_dict.update({0:""})

        insert_data_list = []
        update_data_list = []
        delete_data_list = []
        LX_data = []
        for _data in response_lx_planpurchase:
            for _data_1 in range(len(_data["item_list"])):
                # 总金额,品牌,供应商报价,参考价,结束差异量,分类,材质,识别码
                if len(_data["item_list"][_data_1]["attribute"]) == 0:
                    attribute = ""
                else:
                    attribute = _data["item_list"][_data_1]["attribute"][0]["attr_name"] + ":" + _data["item_list"][_data_1]["attribute"][0]["attr_value"]
                if len(_data["item_list"][_data_1]["msku"]) == 0:
                    MSKU = ""
                else:
                    MSKU = _data["item_list"][_data_1]["msku"][0]
                if _data["is_tax"] == 0:
                    hsdj = 0
                    dj = float(_data["item_list"][_data_1]["price"])
                else:
                    hsdj = float(_data["item_list"][_data_1]["price"])
                    dj = 0
                try:
                    sid_name = sid_dict[_data["item_list"][_data_1]["sid"]]
                except:
                    sid_name = ""
                if _data["status"] == 124:
                    data_status = "(审批流)作废"
                    continue
                elif _data["status"] == 3:
                    data_status = "待提交"
                elif _data["status"] == 1:
                    data_status = "待下单 - 已审核"
                elif _data["status"] == 2:
                    data_status = "待签收(待到货) - 已下单"
                elif _data["status"] == 9:
                    data_status = "完成"
                    continue
                elif _data["status"] == 121:
                    data_status = "(审批流)待审核"
                elif _data["status"] == 122:
                    data_status = "(审批流)驳回"
                    continue
                else:
                    data_status = "作废"
                    continue
                fields = {
                        "ID":_data["item_list"][_data_1]["id"],
                        "采购单号":_data["order_sn"],
                        "供应商":_data["supplier_name"],    
                        "仓库":_data["ware_house_name"],
                        "采购员":_data["opt_uid"],
                        "SKU":_data["item_list"][_data_1]["sku"],
                        "品名":_data["item_list"][_data_1]["product_name"],
                        "SPU":_data["item_list"][_data_1]["spu"],
                        "款名":_data["item_list"][_data_1]["spu_name"],
                        "属性":attribute,
                        "店铺":sid_name,
                        "MSKU":MSKU,
                        "FNSKU":_data["item_list"][_data_1]["fnsku"],
                        "型号":_data["item_list"][_data_1]["model"],
                        "单价":dj,
                        "含税单价":hsdj,
                        "采购量":_data["item_list"][_data_1]["quantity_real"],
                        "税率":float(_data["item_list"][_data_1]["tax_rate"]),
                        "金额":_data["item_list"][_data_1]["quantity_real"],
                        "价税合计":_data["item_list"][_data_1]["amount"],
                        "到货量":_data["item_list"][_data_1]["quantity_entry"],
                        "待到货量":_data["item_list"][_data_1]["quantity_receive"],
                        "换货量":_data["item_list"][_data_1]["quantity_exchange"],
                        "产品备注":_data["item_list"][_data_1]["remark"],
                        "预计到货时间":_data["item_list"][_data_1]["expect_arrive_time"],
                        "待到货量":_data["item_list"][_data_1]["quantity_receive"],
                        "状态":data_status
                        }
                if _data["item_list"][_data_1]["id"] not in FeishuReult:
                    insert_data_list.append({
                        "fields":fields
                        })
                else:
                    update_data_list.append({
                        "record_id":FeishuReult[_data["item_list"][_data_1]["id"]],
                        "fields":fields
                    })
                LX_data.append(_data["item_list"][_data_1]["id"])

        for _data in list(set(FeishuReult.keys()) - set(LX_data)):
            delete_data_list.append(FeishuReult[_data])

        if len(insert_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
                payload_dict = {"records":_data}
                response = feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblsiC3jAdIqbbfG', payload_dict = payload_dict)
                print(response)
        if len(update_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data}
                response = feishuapi().__postUpdatesDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblsiC3jAdIqbbfG', payload_dict = payload_dict)
                print(response)
        if len(delete_data_list) != 0:
            payload_dict = {"records":delete_data_list}
            response = feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblsiC3jAdIqbbfG', payload_dict = payload_dict)
            print(response)