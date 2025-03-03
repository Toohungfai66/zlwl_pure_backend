from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta  
import json
import requests

class cg_planpurchase:

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

    def FEISHU_FBA_DICT(self) -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        while has_more:
            filter_condition = {
                "field_names": [
                    "计划编号",
                ],
                "filter": {
                    "conjunction": "and",
                    "conditions": []
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblMT8KYNHF28z5Z', filter_condition=filter_condition, page_token = page_token, page_size=500)
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
            result_dict.update({feishu_data["fields"]["计划编号"][0]["text"]:feishu_data["record_id"]})
        return result_dict

    def main(self):
        date_str = datetime.now()
        end_date = date_str.strftime("%Y-%m-%d")
        start_date = date_str - timedelta(days=365)
        start_date = start_date.strftime("%Y-%m-%d")
        # 采购计划领星数据整理
        response_lx_planpurchase = lingxingapi().__getPlanPurchase__(start_date=start_date,end_date=end_date,status=[2])
        FeishuReult = self.FEISHU_FBA_DICT()

        insert_data_list = []
        update_data_list = []
        delete_data_list = []
        LX_data = []
        for _data in response_lx_planpurchase:
            try:
                MSKU = _data["msku"][0]
            except:
                MSKU = ""
            try:
                profit = _data["attribute"][0]["attr_value"]
            except:
                profit = ""
            fields = {
                "计划编号":_data["plan_sn"],
                "创建批次号":_data["ppg_sn"],
                "产品图片":_data["pic_url"],
                "SKU":_data["sku"],
                "MSKU":MSKU,
                "FNSKU":_data["fnsku"],
                "款名":_data["spu_name"],
                "SPU":_data["spu"],
                "品名":_data["product_name"],
                "国家":_data["marketplace"],
                "店铺":_data["seller_name"],
                "供应商":_data["supplier_name"],
                "业务员":_data["creator_real_name"],
                "采购员":_data["cg_opt_username"],
                "仓库":_data["warehouse_name"],
                "计划采购量":_data["quantity_plan"],
                "属性":profit,
                "创建时间":_data["create_time"],
                "数据状态":_data["status_text"]
                }
            if _data["plan_sn"] not in FeishuReult:
                insert_data_list.append({
                    "fields":fields
                    })
            else:
                update_data_list.append({
                    "record_id":FeishuReult[_data["plan_sn"]],
                    "fields":fields
                })
            LX_data.append(_data["plan_sn"])

        for _data in list(set(FeishuReult.keys()) - set(LX_data)):
            delete_data_list.append(FeishuReult[_data])

        if len(insert_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
                payload_dict = {"records":_data}
                feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblMT8KYNHF28z5Z', payload_dict = payload_dict)
        if len(update_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data}
                feishuapi().__postUpdatesDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblMT8KYNHF28z5Z', payload_dict = payload_dict)
        if len(delete_data_list) != 0:
            payload_dict = {"records":delete_data_list}
            feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblMT8KYNHF28z5Z', payload_dict = payload_dict)