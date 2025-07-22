from .FeiShuAPI import feishuapi
from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta  
import json
import requests
import re

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

    def FEISHU_FBA_DICT(self, project_name) -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        if project_name == "one":
            field_names = ["ID"]
        elif project_name == "two":
            field_names = [
                    "ID",
                    "周期(第一周)",
                    "周期(第二周)",
                    "周期(第三周)",
                    "周期(第四周)",
                    "周期(第五周)",
                    "周期(第六周)",
                    "周期(第七周)",
                    "周期(第八周)",
                    "周期(第九周)",
                    "周期(第十周)",
                    "周期(第十一周)",
                    "周期(第十二周)",
                    "实际到货量(第一周)",
                    "实际到货量(第二周)",
                    "实际到货量(第三周)",
                    "实际到货量(第四周)",
                    "实际到货量(第五周)",
                    "实际到货量(第六周)",
                    "实际到货量(第七周)",
                    "实际到货量(第八周)",
                    "实际到货量(第九周)",
                    "实际到货量(第十周)",
                    "实际到货量(第十一周)",
                    "实际到货量(第十二周)",
                    "到货量",
                    "SKU",
                    "采购单号"
                ]
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
            if project_name == "one":
                result_dict.update({feishu_data["fields"]["ID"]:feishu_data["record_id"]})
            elif project_name == "two":
                if "实际到货量(第一周)" in feishu_data["fields"]:
                    data_sj_1 = feishu_data["fields"]["实际到货量(第一周)"]
                else:
                    data_sj_1 = 0
                if "实际到货量(第二周)" in feishu_data["fields"]:
                    data_sj_2 = feishu_data["fields"]["实际到货量(第二周)"]
                else:
                    data_sj_2 = 0
                if "实际到货量(第三周)" in feishu_data["fields"]:
                    data_sj_3 = feishu_data["fields"]["实际到货量(第三周)"]
                else:
                    data_sj_3 = 0
                if "实际到货量(第四周)" in feishu_data["fields"]:
                    data_sj_4 = feishu_data["fields"]["实际到货量(第四周)"]
                else:
                    data_sj_4 = 0
                if "实际到货量(第五周)" in feishu_data["fields"]:
                    data_sj_5 = feishu_data["fields"]["实际到货量(第五周)"]
                else:
                    data_sj_5 = 0
                if "实际到货量(第六周)" in feishu_data["fields"]:
                    data_sj_6 = feishu_data["fields"]["实际到货量(第六周)"]
                else:
                    data_sj_6 = 0
                if "实际到货量(第七周)" in feishu_data["fields"]:
                    data_sj_7 = feishu_data["fields"]["实际到货量(第七周)"]
                else:
                    data_sj_7 = 0
                if "实际到货量(第八周)" in feishu_data["fields"]:
                    data_sj_8 = feishu_data["fields"]["实际到货量(第八周)"]
                else:
                    data_sj_8 = 0
                if "实际到货量(第九周)" in feishu_data["fields"]:
                    data_sj_9 = feishu_data["fields"]["实际到货量(第九周)"]
                else:
                    data_sj_9 = 0
                if "实际到货量(第十周)" in feishu_data["fields"]:
                    data_sj_10 = feishu_data["fields"]["实际到货量(第十周)"]
                else:
                    data_sj_11 = 0
                if "实际到货量(第十一周)" in feishu_data["fields"]:
                    data_sj_11 = feishu_data["fields"]["实际到货量(第十一周)"]
                else:
                    data_sj_11 = 0
                if "实际到货量(第十二周)" in feishu_data["fields"]:
                    data_sj_12 = feishu_data["fields"]["实际到货量(第十二周)"]
                else:
                    data_sj_12 = 0
                result_dict.update({feishu_data["fields"]["ID"]:{
                    "record_id":feishu_data["record_id"],
                    "周期(第一周)":feishu_data["fields"]["周期(第一周)"]['value'][0]["text"],
                    "周期(第二周)":feishu_data["fields"]["周期(第二周)"]['value'][0]["text"],
                    "周期(第三周)":feishu_data["fields"]["周期(第三周)"]['value'][0]["text"],
                    "周期(第四周)":feishu_data["fields"]["周期(第四周)"]['value'][0]["text"],
                    "周期(第五周)":feishu_data["fields"]["周期(第五周)"]['value'][0]["text"],
                    "周期(第六周)":feishu_data["fields"]["周期(第六周)"]['value'][0]["text"],
                    "周期(第七周)":feishu_data["fields"]["周期(第七周)"]['value'][0]["text"],
                    "周期(第八周)":feishu_data["fields"]["周期(第八周)"]['value'][0]["text"],
                    "周期(第九周)":feishu_data["fields"]["周期(第九周)"]['value'][0]["text"],
                    "周期(第十周)":feishu_data["fields"]["周期(第十周)"]['value'][0]["text"],
                    "周期(第十一周)":feishu_data["fields"]["周期(第十一周)"]['value'][0]["text"],
                    "周期(第十二周)":feishu_data["fields"]["周期(第十二周)"]['value'][0]["text"],
                    "实际到货量(第一周)":data_sj_1,
                    "实际到货量(第二周)":data_sj_2,
                    "实际到货量(第三周)":data_sj_3,
                    "实际到货量(第四周)":data_sj_4,
                    "实际到货量(第五周)":data_sj_5,
                    "实际到货量(第六周)":data_sj_6,
                    "实际到货量(第七周)":data_sj_7,
                    "实际到货量(第八周)":data_sj_8,
                    "实际到货量(第九周)":data_sj_9,
                    "实际到货量(第十周)":data_sj_10,
                    "实际到货量(第十一周)":data_sj_11,
                    "实际到货量(第十二周)":data_sj_12,
                    "到货量":feishu_data["fields"]["到货量"],
                    "SKU":feishu_data["fields"]["SKU"][0]["text"],
                    "采购单号":feishu_data["fields"]["采购单号"][0]["text"]
                    }})
            else:
                pass
        return result_dict

    def main(self):
        date_str = datetime.now()
        end_date = date_str.strftime("%Y-%m-%d")
        start_date = date_str - timedelta(days=365)
        start_date = start_date.strftime("%Y-%m-%d")
        name_open_id_dict = {}
        for _data in ["od-027e3daf1d2d45b1cb46cc4ef3bb4f30"]:
            department_response = feishuapi().__getSubDepartmentId__(department_id=_data)
            for _data_1 in department_response["data"]["items"]:
                departmentuser = feishuapi().__getDepartmentalUsers__(payload_dict={"department_id":_data_1["open_department_id"],"page_size":50})
                if "items" not in departmentuser["data"]:
                    continue
                for _data_2 in departmentuser["data"]["items"]:
                    name_open_id_dict[_data_2["name"]] = _data_2["open_id"]
        for _data_1 in ["od-655b56ce1287a45e5df27540730e9a51","od-4639905de3a8bf8815b99d901c0707ae","od-0eefd2e0318a6e509155556d3bf24c3e","od-2a479acc0716769fd28db5351e1df082","od-55e70d9a5a94dac7accf071d36a32b15","od-928bb13cb6194ce172a8472242c97427"]:
            departmentuser = feishuapi().__getDepartmentalUsers__(payload_dict={"department_id":_data_1,"page_size":50})
            if "items" not in departmentuser["data"]:
                continue
            for _data_2 in departmentuser["data"]["items"]:
                name_open_id_dict[_data_2["name"]] = _data_2["open_id"]
        # 采购计划领星数据整理
        response_lx_planpurchase = lingxingapi().__getOrderPurchase__(start_date=start_date,end_date=end_date)

        FeishuReult = self.FEISHU_FBA_DICT(project_name = "one")

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
            # 排除RT与SX供应商之外的其他供应商
            # if "RT" not in _data["supplier_name"] and "SX" not in _data["supplier_name"]:
            #     continue
            for _data_1 in range(len(_data["item_list"])):
                # 去除待到货为0的数据
                if _data["item_list"][_data_1]["quantity_receive"] == 0:
                    continue
                # 排除品名包含辅料的数据
                if "辅料" in _data["item_list"][_data_1]["product_name"]:
                    continue
                if len(_data["item_list"][_data_1]["attribute"]) == 0:
                    attribute = ""
                else:
                    attribute = _data["item_list"][_data_1]["attribute"][0]["attr_name"] + ":" + _data["item_list"][_data_1]["attribute"][0]["attr_value"]
                if len(_data["item_list"][_data_1]["msku"]) == 0:
                    MSKU = ""
                else:
                    MSKU = _data["item_list"][_data_1]["msku"][0]
                if _data["is_tax"] == 0:
                    dj = float(_data["item_list"][_data_1]["price"])
                else:
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
                fzr_list = []
                for _data_2 in _data["principal_uids"]:
                    if _data_2["name"] == "余琛瑶":
                        fzr_list.append({"id":name_open_id_dict["余琛瑶Cali"]})
                        continue
                    elif _data_2["name"] == "刘捷Leo":
                        fzr_list.append({"id":name_open_id_dict["刘捷"]})
                        continue
                    elif _data_2["name"] == "黄艳辉":
                        fzr_list.append({"id":name_open_id_dict["唐夜娜"]})
                        continue
                    elif _data_2["name"] == "孔子园":
                        fzr_list.append({"id":name_open_id_dict["李佳喜"]})
                        continue
                    elif _data_2["name"] == "王胜成":
                        fzr_list.append({"id":name_open_id_dict["邓广青"]})
                        continue
                    elif _data_2["name"] == "李霞":
                        fzr_list.append({"id":name_open_id_dict["邓广青"]})
                        continue
                    try:
                        fzr_list.append({"id":name_open_id_dict[_data_2["name"]]})
                    except:
                        continue
                fields = {
                        "ID":_data["item_list"][_data_1]["id"],
                        "采购单号":_data["order_sn"],
                        "计划编号":_data["item_list"][_data_1]["plan_sn"],
                        "供应商":_data["supplier_name"],    
                        "仓库":_data["ware_house_name"],
                        # "采购员":_data["opt_uid"],
                        "SKU":_data["item_list"][_data_1]["sku"],
                        "品名":_data["item_list"][_data_1]["product_name"],
                        "SPU":_data["item_list"][_data_1]["spu"],
                        "款名":_data["item_list"][_data_1]["spu_name"],
                        "属性":attribute,
                        "店铺":sid_name,
                        "负责人":_data["principal_uids"][0]["name"],
                        "负责人(人员)":fzr_list,
                        # "MSKU":MSKU,
                        "FNSKU":_data["item_list"][_data_1]["fnsku"],
                        # "型号":_data["item_list"][_data_1]["model"],
                        "单价":dj,
                        # "含税单价":hsdj,
                        "采购量":_data["item_list"][_data_1]["quantity_real"],
                        "箱数":_data["item_list"][_data_1]["cases_num"],
                        # "税率":float(_data["item_list"][_data_1]["tax_rate"]),
                        # "金额":float(_data["total_price"]),
                        "价税合计":_data["item_list"][_data_1]["amount"],
                        "到货量":_data["item_list"][_data_1]["quantity_entry"],
                        "系统待到货量":_data["item_list"][_data_1]["quantity_receive"],
                        "换货量":_data["item_list"][_data_1]["quantity_exchange"],
                        "产品备注":_data["item_list"][_data_1]["remark"],
                        "预计到货时间":_data["item_list"][_data_1]["expect_arrive_time"],
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
                print(feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblsiC3jAdIqbbfG', payload_dict = payload_dict))
        if len(update_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data}
                print(feishuapi().__postUpdatesDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblsiC3jAdIqbbfG', payload_dict = payload_dict))
        if len(delete_data_list) != 0:
            for _data in [delete_data_list[i:i + 500] for i in range(0, len(delete_data_list), 500)]:
                payload_dict = {"records":_data}
                print(feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblsiC3jAdIqbbfG', payload_dict = payload_dict))
    
        FeishuReult = self.FEISHU_FBA_DICT(project_name = "two")
        # 计算昨天的日期
        yesterday = datetime.now() - timedelta(days=1)
        # 格式化输出昨天的日期
        current_date = yesterday.strftime("%Y-%m-%d")

        # current_date = "2025-05-26"

        getorders = lingxingapi().__getOrders__(start_date=current_date,end_date=current_date)
        result_dict_getorders = {}
        for _data in getorders:
            for _data_1 in _data["item_list"]:
                orde_id = _data["purchase_order_sn"] + _data_1["sku"]
                rkl = _data_1["product_total"]
                if orde_id in result_dict_getorders:
                    result_dict_getorders.update({orde_id:result_dict_getorders[orde_id] + rkl})
                else:
                    result_dict_getorders.update({orde_id:rkl})
        update_data_list = []
        for _data in FeishuReult:
            if FeishuReult[_data]["采购单号"]+FeishuReult[_data]["SKU"] not in result_dict_getorders:
                continue
            fields_name_num = ""
            for _data_1 in FeishuReult[_data]:
                if "周期" not in _data_1 :
                    continue
                if current_date in FeishuReult[_data][_data_1]:
                    fields_name_num = re.findall("\(.+\)",_data_1)[0]
                    break
            if len(fields_name_num) == 0:
                continue
            else:
                fields = {
                    "实际到货量"+fields_name_num : FeishuReult[_data]["实际到货量"+fields_name_num] + result_dict_getorders[FeishuReult[_data]["采购单号"]+FeishuReult[_data]["SKU"]]
                }
            update_data_list.append({
                "record_id":FeishuReult[_data]["record_id"],
                "fields":fields
            })
        if len(update_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data}
                print(feishuapi().__postUpdatesDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblsiC3jAdIqbbfG', payload_dict = payload_dict))