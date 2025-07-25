from .FeiShuAPI import feishuapi
import json
import requests
import numpy as np

class cg_supplier:

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

    def FEISHU_FBA_DICT(self, app_token,table_id,project) -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        if project == "CGD":
            field_names = ["品名","SKU"]
        elif project == "RT":
            field_names = ['SKU','品名',"SPU款名",'SPU','规格','颜色']
        elif project == "SX":
            field_names = ['SKU','品名','SPU款名','SPU','规格','颜色']
        else:
            field_names = []
        while has_more:
            filter_condition = {
                "field_names": field_names,
                "filter": {
                    "conjunction": "and",
                    "conditions": []
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = app_token, table_id = table_id, filter_condition=filter_condition, page_token = page_token, page_size=500)
            if response['code'] == 0:
                feishu_datas.extend(response['data']['items'])
                has_more = response['data']['has_more']
                if has_more == False:
                    break
                page_token = response['data']['page_token']
            else:
                raise Exception(response['msg'])
        result_dict = {}
        if project == "CGD":
            for feishu_data in feishu_datas:
                result_dict.update({feishu_data["record_id"]:{"品名":feishu_data["fields"]["品名"][0]["text"],"SKU":feishu_data["fields"]["SKU"][0]["text"]}})
        elif project == "RT":
            for feishu_data in feishu_datas:
                if "SKU" not in feishu_data["fields"]:
                    continue
                ls_dict = {"SKU":feishu_data["fields"]["SKU"][0]["text"],"品名":feishu_data["fields"]["品名"][0]["text"],"SPU":feishu_data["fields"]["SPU"][0]["text"],"SPU款名":feishu_data["fields"]["SPU款名"][0]["text"]}
                if "规格" in feishu_data["fields"]:
                    ls_dict.update({"规格":feishu_data["fields"]["规格"][0]["text"]})
                else:
                    ls_dict.update({"规格":""})
                if "颜色" in feishu_data["fields"]:
                    ls_dict.update({"颜色":feishu_data["fields"]["颜色"][0]["text"]})
                else:
                    ls_dict.update({"颜色":""})
                result_dict.update({feishu_data["record_id"]:ls_dict})
        elif project == "SX":
            for feishu_data in feishu_datas:
                ls_dict = {"SPU款名":feishu_data["fields"]["SPU款名"][0]["text"],"SKU":feishu_data["fields"]["SKU"][0]["text"],
                           "品名":feishu_data["fields"]["品名"][0]["text"],"SPU":feishu_data["fields"]["SPU"][0]["text"]}
                if "规格" in feishu_data["fields"]:
                    ls_dict.update({"规格":feishu_data["fields"]["规格"][0]["text"]})
                else:
                    ls_dict.update({"规格":""})
                if "颜色" in feishu_data["fields"]:
                    ls_dict.update({"颜色":feishu_data["fields"]["颜色"][0]["text"]})
                else:
                    ls_dict.update({"颜色":""})
                result_dict.update({feishu_data["record_id"]:ls_dict})
        else:
            pass
        return result_dict
    
    def main(self):
        FeishuReult_CGD = self.FEISHU_FBA_DICT(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblsiC3jAdIqbbfG', project = 'CGD')
        FeishuReult_SX = self.FEISHU_FBA_DICT(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblpg9U6ZRi5cjbN', project = "SX")
        FeishuReult_RT = self.FEISHU_FBA_DICT(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblaPEjdkB71y7xL', project = "RT")

        update_data_list = []
        SX_dict = {}
        RT_dict = {}

        for _data in FeishuReult_SX:
            if FeishuReult_SX[_data]["品名"] in SX_dict:
                SX_dict.update({FeishuReult_SX[_data]["品名"]:{"规格":list(set(SX_dict[FeishuReult_SX[_data]["品名"]]["规格"] + [FeishuReult_SX[_data]["规格"]])),"颜色":list(set(SX_dict[FeishuReult_SX[_data]["品名"]]["颜色"] + [FeishuReult_SX[_data]["颜色"]]))}})
            else:
                SX_dict.update({FeishuReult_SX[_data]["品名"]:{"规格":[FeishuReult_SX[_data]["规格"]],"颜色":[FeishuReult_SX[_data]["颜色"]]}})

        # for _data in FeishuReult_RT:
        #     if FeishuReult_RT[_data]["型号"] in RT_dict:
        #         RT_dict.update({FeishuReult_RT[_data]["型号"]:{"规格":list(set(RT_dict[FeishuReult_RT[_data]["型号"]]["规格"] + [FeishuReult_RT[_data]["规格"]])),"颜色":list(set(RT_dict[FeishuReult_RT[_data]["型号"]]["颜色"] + [FeishuReult_RT[_data]["颜色"]]))}})
        #     else:
        #         RT_dict.update({FeishuReult_RT[_data]["型号"]:{"规格":[FeishuReult_RT[_data]["规格"]],"颜色":[FeishuReult_RT[_data]["颜色"]]}})

        # RT_key_list = sorted(RT_dict.keys(), key=len, reverse=True)

        for _data in FeishuReult_RT:
            if FeishuReult_RT[_data]["SKU"] in RT_dict:
                RT_dict.update({FeishuReult_RT[_data]["SKU"]:{"规格":list(set(RT_dict[FeishuReult_RT[_data]["SKU"]]["规格"] + [FeishuReult_RT[_data]["规格"]])),"颜色":list(set(RT_dict[FeishuReult_RT[_data]["SKU"]]["颜色"] + [FeishuReult_RT[_data]["颜色"]]))}})
            else:
                RT_dict.update({FeishuReult_RT[_data]["SKU"]:{"规格":[FeishuReult_RT[_data]["规格"]],"颜色":[FeishuReult_RT[_data]["颜色"]]}})

        for _data in FeishuReult_CGD:
            fields = {}
            # for _data_1 in RT_key_list:
            #     if _data_1 in FeishuReult_CGD[_data]["品名"]:
            #         CM = ""
            #         YS = ""
            #         for _data_2 in sorted([i for i in RT_dict[_data_1]["规格"] if not (isinstance(i, float) and np.isnan(i))], key=len, reverse=True):
            #             if len(_data_2) == 0:
            #                 continue
            #             if _data_2 in FeishuReult_CGD[_data]["品名"]:
            #                 CM = CM + _data_2 + ","
            #         for _data_2 in sorted([i for i in RT_dict[_data_1]["颜色"] if not (isinstance(i, float) and np.isnan(i))], key=len, reverse=True):
            #             if len(_data_2) == 0:
            #                 continue
            #             if _data_2 in FeishuReult_CGD[_data]["品名"]:
            #                 YS = YS + _data_2 + ","
            #         fields.update({"尺码":CM[:-1],"颜色":YS[:-1]})
            #         if len(fields) != 0:
            #             for _data_2 in FeishuReult_RT:
            #                 if FeishuReult_RT[_data_2]["型号"] == _data_1 and FeishuReult_RT[_data_2]["规格"] == fields["尺码"] and FeishuReult_RT[_data_2]["颜色"] == fields["颜色"]:
            #                     fields.update({"物料编码":FeishuReult_RT[_data_2]["物料编码"],"物料名称":FeishuReult_RT[_data_2]["物料名称"],"型号":FeishuReult_RT[_data_2]["型号"]})
            #             update_data_list.append({
            #                 "record_id":_data,
            #                 "fields":fields
            #             })
            #         break
            for _data_1 in FeishuReult_RT:
                if FeishuReult_RT[_data_1]["SKU"] == FeishuReult_CGD[_data]["SKU"]:
                    fields.update({"尺码":FeishuReult_RT[_data_1]["规格"],"颜色":FeishuReult_RT[_data_1]["颜色"],"SPU款名":FeishuReult_RT[_data_1]["SPU款名"],
                                    "型号":FeishuReult_RT[_data_1]["SPU"]})
            if len(fields) == 0:
                for _data_1 in FeishuReult_SX:
                    if FeishuReult_SX[_data_1]["品名"] == FeishuReult_CGD[_data]["品名"]:
                        fields.update({"尺码":FeishuReult_SX[_data_1]["规格"],"颜色":FeishuReult_SX[_data_1]["颜色"],"SPU款名":FeishuReult_SX[_data_1]["SPU款名"],
                                       "型号":FeishuReult_SX[_data_1]["SPU"]})
            if len(fields) != 0:
                update_data_list.append({
                    "record_id":_data,
                    "fields":fields
                })
                
        if len(update_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data}
                print(feishuapi().__postUpdatesDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblsiC3jAdIqbbfG', payload_dict = payload_dict))