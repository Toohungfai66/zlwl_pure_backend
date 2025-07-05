from .FeiShuAPI import feishuapi
from datetime import datetime, timedelta
import json,requests,re,joblib,os,math
import pandas as pd
import xgboost as xgb

class salesforecast:

    def __init__(self):
        pass

    def get_date_range(self, start_date_str, days) -> list:
        # 将输入的日期字符串转换为 datetime 对象
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        date_range = []
        for i in range(days):
            # 计算未来第 i 天的日期
            future_date = start_date + timedelta(days=i)
            # 将日期转换为字符串格式并添加到列表中
            date_range.append(future_date.strftime('%Y-%m-%d'))
        return date_range

    def get_bitable_datas(self, app_token, table_id, filter_condition, page_token='', page_size=20) -> json:

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search?page_size={page_size}&page_token={page_token}&user_id_type=user_id"
        payload = json.dumps(filter_condition)
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
            filter_condition = {
                "field_names": [
                    "父ASIN",
                    "店铺",
                    "日期",
                    "程序模型周预估(父ASIN)"
                ],
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
        for feishu_data in feishu_datas:
            if "程序模型周预估(父ASIN)" in feishu_data["fields"]:
                continue
            if "父ASIN" not in feishu_data["fields"] or "店铺" not in feishu_data["fields"]:
                continue
            result_dict.update({
                feishu_data["record_id"]:{
                    "父ASIN":feishu_data["fields"]["父ASIN"][0]["text"],
                    "店铺":feishu_data["fields"]["店铺"][0]["text"],
                    "日期":feishu_data["fields"]["日期"][0]["text"]
                    }
                })
        return result_dict
    
    def get_dates_in_range(self, date_range_str):
        """从日期区间字符串获取详细日期列表"""
        # 分割日期区间
        start_str, end_str = date_range_str.split('-')
        
        # 解析开始和结束日期（处理可能的不同分隔符）
        start_date = datetime.strptime(start_str, '%Y.%m.%d')
        end_date = datetime.strptime(end_str, '%Y.%m.%d')
        
        # 生成日期列表
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        return date_list

    def main(self):
        for _data in {"事业一部":[],"事业二部":[],"事业三部":[],"事业四部":[],"事业五部":[],"事业六部":[],"事业八部":[],"事业九部":[],"事业十部":[]}:
            if _data == "事业一部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tblZfMM49mxJjoaX"
            elif _data == "事业二部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tblsYM9fjAqtaq0h"
            elif _data == "事业三部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tblFZ2wocAMljZ5m"
            elif _data == "事业四部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tbl3o8PwMlTsAGdv"
            elif _data == "事业五部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tbleE0SDumXNLLAe"
            elif _data == "事业六部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tblyD4f81VxbAXHx"
            elif _data == "事业八部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tblsmKm5K61c2b5I"
            elif _data == "事业九部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tblvmu45KnNtfS6g"
            elif _data == "事业十部":
                app_token="TxmobrecbaIyblsh9p8cv3k6n3f"
                table_id="tblTz9Z3yR1s7aRi"
            else:
                continue
            update_data_list = []
            feishudata = self.FEISHU_FBA_DICT(app_token=app_token,table_id=table_id)
            for _data in feishudata:
                pkl_name = feishudata[_data]["父ASIN"] + "," + feishudata[_data]["店铺"]
                pkl_name = str(pkl_name).replace('/', '-')
                if pkl_name + ".pkl" not in os.listdir("C:\\Project\\zlwl_pure_backend\\PMC\\static\\ParentAsin_fiels_model"):
                    update_data_list.append({
                        "record_id":_data,
                        "fields": {"程序模型周预估(父ASIN)":0}
                    }) 
                    continue
                df = pd.DataFrame(columns=["日期"])
                for _date in self.get_dates_in_range(feishudata[_data]["日期"]):
                    df.loc[len(df)] = [_date]
                df['日期'] = pd.to_datetime(df['日期'])
                df['年'] = df['日期'].dt.year
                df['月'] = df['日期'].dt.month
                df['日'] = df['日期'].dt.day
                df['星期几'] = df['日期'].dt.dayofweek
                # 定义季节映射
                season_mapping = {1: '冬季', 2: '冬季', 3: '春季', 4: '春季', 5: '春季', 6: '夏季', 
                                7: '夏季', 8: '夏季', 9: '秋季', 10: '秋季', 11: '秋季', 12: '冬季'}
                df['季节'] = df['月'].map(season_mapping)

                # 对季节进行独热编码
                df = pd.get_dummies(df, columns=['季节'])
                loaded_model = joblib.load(f'C:\\Project\\zlwl_pure_backend\\PMC\\static\\ParentAsin_fiels_model\\{pkl_name}.pkl')
                # 提取特征列
                X = df.drop(columns=['日期'])
                # 将特征数据转换为 DMatrix 格式
                dmatrix_X = xgb.DMatrix(X) 
                # 使用加载的模型进行预测
                try:
                    y_pred = loaded_model.predict(dmatrix_X)
                except:
                    update_data_list.append({
                    "record_id":_data,
                    "fields": {
                        "程序模型周预估(父ASIN)":0
                        }
                    }) 
                    continue
                # 将预测结果添加到 DataFrame 中
                df['预测销量'] = y_pred
                sum_sala = df['预测销量'].sum()
                update_data_list.append({
                    "record_id":_data,
                    "fields": {
                        "程序模型周预估(父ASIN)":math.ceil(sum_sala)
                    }
                }) 
            if len(update_data_list) != 0:
                # 以500为划分，更新回飞书表格，正常的更新
                for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                    payload_dict = {"records":_data}
                    print(feishuapi().__postUpdatesDatas__(app_token = app_token, table_id = table_id, payload_dict = payload_dict))