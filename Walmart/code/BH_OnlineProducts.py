from .LingXingAPI import lingxingapi
from .FeiShuAPI import feishuapi
import requests
import json

class bh_onlineproducts:

    def __init__(self):
        pass

    def get_bitable_datas(self, app_token, table_id, page_token='', page_size=20) -> json:

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search?page_size={page_size}&page_token={page_token}&user_id_type=user_id"
        payload = json.dumps({})
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {feishuapi().__getTenantAccessToken__()}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()

    def FEISHU_FBA_DICT(self,app_token,table_id) -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        while has_more:
            response = self.get_bitable_datas(app_token = app_token, table_id = table_id, page_token = page_token, page_size=500)
            if response['code'] == 0:
                feishu_datas.extend(response['data']['items'])
                has_more = response['data']['has_more']
                if has_more == False:
                    break
                page_token = response['data']['page_token']
            else:
                raise Exception(response['msg'])
        result_list = []
        for feishu_data in feishu_datas:
            result_list.append(feishu_data["record_id"])
        return result_list
    
    def main(self):
        lingxingresult = lingxingapi().__getOnlineProducts__(status=[0,3], store_ids=["110293196894021120", "110293197760128000", "110578840592464896", "110578848461229056"])
        BH_insert_data_list = []
        for _data in lingxingresult:
            if "delete" in str(_data["title"]).lower():
                continue
            # 基础信息
            pay_dict = {
                "MSKU":_data["msku"],
                "图片URL":_data["picture_url"],
                "标题":_data["title"],
                "SKU":_data["local_sku"],
                "品名":_data["local_name"],
                "状态":_data["status_name"],
                "店铺":_data["store_name"],
                "价格":float(_data["price"]),
                "WFS可售数量":_data["wfs_available_quantity"],
                "Buy Box价格":float(_data["buy_box_price"]),
                "Buy Box运费":float(_data["buy_box_shipping_price"]),
                "GTIN":_data["gtin"],
                "UPC":_data["upc"],
                "评论数":int(_data["review_count"]),
                "品牌":_data["brand"],
                "发货方式":_data["fulfillment_type_name"],
                "竞品价格":float(_data["competitor_price"]),
                "竞品运费":float(_data["competitor_ship_price"]),
            }
            if len(_data["average_rating"]) != 0:
                pay_dict["评分"] = float(_data["average_rating"])
            else:
                pay_dict["评分"] = 0
            BH_insert_data_list.append({"fields": pay_dict})

        delete_data_list = self.FEISHU_FBA_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tblWOZnl245oOkJj")
        for _data in [delete_data_list[i:i + 500] for i in range(0, len(delete_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblWOZnl245oOkJj', payload_dict = payload_dict)

        if len(BH_insert_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [BH_insert_data_list[i:i + 500] for i in range(0, len(BH_insert_data_list), 500)]:
                payload_dict = {"records":_data}
                print(feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblWOZnl245oOkJj', payload_dict = payload_dict))