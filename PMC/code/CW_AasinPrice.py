from .FeiShuAPI import feishuapi
import json
import requests
import os

class cw_asinprice:

    def __init__(self):
        pass

    # 查询记录
    def get_bitable_datas(self, app_token, table_id, page_token='', page_size=20,filter_condition={}):
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search?page_size={page_size}&page_token={page_token}&user_id_type=user_id"
        payload = json.dumps(filter_condition)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {feishuapi().__getTenantAccessToken__()}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()
    
    def main(self):
        page_token = ''
        has_more = True
        feishu_datas = []
        # 调用外部API获取数据
        filter_condition = {
            "field_names": ["子ASIN","店铺","广告费比%","退款促销费比%","佣金费比%","订阅费比%","优惠券费比%","秒杀费比%","FBA仓储费比%","其他费比%","现金费比%","移除费比%","经营分摊费比%","采购单价￥","实重(商品)","头程均价(含关税)￥","尾程费(原币)","目前在售价(原币)","汇率","VAT税率"],
            "filter": {
                "conjunction": "and",
                "conditions": []
            },
            "automatic_fields": "false"
        }
        while has_more:
            response = self.get_bitable_datas(app_token="XjL9biLNPaja1Tsb0vRcGGSFnLg",table_id="tbl9knq0KwPnmA3U",page_size=500,filter_condition=filter_condition,page_token = page_token,)
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
            if "子ASIN" not in  feishu_data["fields"] or "店铺" not in feishu_data["fields"]:
                continue
            zz_dict = {}
            if "广告费比%" in feishu_data["fields"]:
                zz_dict['advertising_cost_ratio'] = feishu_data["fields"]["广告费比%"]["value"][0]
            if "退款促销费比%" in feishu_data["fields"]:
                zz_dict['refund_promotion_fee_ratio'] = feishu_data["fields"]["退款促销费比%"]["value"][0]
            if "佣金费比%" in feishu_data["fields"]:
                zz_dict['commission_fee_ratio'] = feishu_data["fields"]["佣金费比%"]["value"][0]
            if "订阅费比%" in feishu_data["fields"]:
                zz_dict['subscription_fee_ratio'] = feishu_data["fields"]["订阅费比%"]["value"][0]
            if "优惠券费比%" in feishu_data["fields"]:
                zz_dict['coupon_fee_ratio'] = feishu_data["fields"]["优惠券费比%"]["value"][0]
            if "秒杀费比%" in feishu_data["fields"]:
                zz_dict['second_kill_cost_ratio'] = feishu_data["fields"]["秒杀费比%"]["value"][0]
            if "FBA仓储费比%" in feishu_data["fields"]:
                zz_dict['FBA_storage_fees_are_lower_than'] = feishu_data["fields"]["FBA仓储费比%"]["value"][0]
            if "其他费比%" in feishu_data["fields"]:
                zz_dict['other_fees_included'] = feishu_data["fields"]["其他费比%"]["value"][0]
            if "现金费比%" in feishu_data["fields"]:
                zz_dict['cash_expense_ratio'] = feishu_data["fields"]["现金费比%"]["value"][0]
            if "移除费比%" in feishu_data["fields"]:
                zz_dict['removal_fee'] = feishu_data["fields"]["移除费比%"]["value"][0]
            if "经营分摊费比%" in feishu_data["fields"]:
                zz_dict['operating_overhead_allocation_ratio'] = feishu_data["fields"]["经营分摊费比%"]["value"][0]
            if "采购单价￥" in feishu_data["fields"]:
                zz_dict['purchase_unit_price'] = feishu_data["fields"]["采购单价￥"]["value"][0]
            if "实重(商品)" in feishu_data["fields"]:
                zz_dict['actual_weight'] = feishu_data["fields"]["实重(商品)"]["value"][0]
            if "头程均价(含关税)￥" in feishu_data["fields"]:
                zz_dict['average_price_for_the_first_leg'] = feishu_data["fields"]["头程均价(含关税)￥"]["value"][0]
            if "尾程费(原币)" in feishu_data["fields"]:
                zz_dict['last_mile_fee'] = feishu_data["fields"]["尾程费(原币)"]
            if "目前在售价(原币)" in feishu_data["fields"]:
                zz_dict['price'] = feishu_data["fields"]["目前在售价(原币)"]
            if "汇率" in feishu_data["fields"]:
                zz_dict['exchange_rate'] = feishu_data["fields"]["汇率"]["value"][0]
            if "VAT税率" in feishu_data["fields"]:
                zz_dict['vat'] = feishu_data["fields"]["VAT税率"]["value"][0]
            result_dict.update({
                feishu_data["fields"]["子ASIN"][0]["text"]+feishu_data["fields"]["店铺"][0]["text"]:zz_dict
            })
        # 先转成 JSON 字符串
        json_str = json.dumps(result_dict, ensure_ascii=False, indent=2)
        current_dir = os.getcwd()  # 返回当前工作目录的绝对路径
        # 再写入文件
        with open(os.path.join(current_dir,"Calculator\status\output.json"), "w", encoding="utf-8") as f:
            f.write(json_str)