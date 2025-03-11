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

    def FEISHU_FBA_DICT(self) -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        while has_more:
            filter_condition = {
                "field_names": [
                    "制单日期",
                    "父ASIN",
                    "ASIN",
                    "MSKU",
                    "当前广告花费(前七天)",
                    "当前大类排名(前七天)",
                    "预计广告花费(周)",
                    "预计大类排名(周)"
                ],
                "filter": {
                    "conjunction": "and",
                    "conditions": []
                },
                "automatic_fields": "false"
            }
            response = self.get_bitable_datas(app_token = 'KVZ9bIrm9azOpqseGx3cIkRfn4f', table_id = 'tblzV27KDQw1t96z', page_token = page_token, filter_condition=filter_condition, page_size=500)
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
            if "预计广告花费(周)" in feishu_data["fields"]:
                GGHF = feishu_data["fields"]["预计广告花费(周)"]
            else:
                try:
                    GGHF = feishu_data["fields"]["当前广告花费(前七天)"]
                except:
                    GGHF = 0
            if "预计大类排名(周)" in feishu_data["fields"]:
                DDPM = feishu_data["fields"]["预计大类排名(周)"]
            else:
                try:
                    DDPM = feishu_data["fields"]["当前大类排名(前七天)"]
                except:
                    DDPM = 0
            try:
                result_dict.update({
                    feishu_data["record_id"]:[
                        feishu_data["fields"]["MSKU"][0]["text"],
                        feishu_data["fields"]["父ASIN"][0]["text"],
                        feishu_data["fields"]["ASIN"][0]["text"],
                        abs(GGHF),
                        DDPM,
                        feishu_data["fields"]["制单日期"][0]["text"]
                        ]
                    })
            except:
                continue
        return result_dict
    def main(self):
        update_data_list = []
        feishudata = self.FEISHU_FBA_DICT()
        for _data in feishudata:
            pkl_name = feishudata[_data][0] + "_" + feishudata[_data][1] + "_" + feishudata[_data][2]
            if pkl_name + ".pkl" not in os.listdir("C:\\Project\\Zlwl\\PMC\\static\\msku_fiels_model"):
                continue
            # 给定的日期
            input_date = feishudata[_data][5]
            date_range_7_days = self.get_date_range(input_date, 7)
            seventy_five_days_later = (datetime.strptime(input_date, '%Y-%m-%d') + timedelta(days=75)).strftime('%Y-%m-%d')
            date_range_75_and_7_days = self.get_date_range(seventy_five_days_later, 7)

            ifnum = 0
            fields = {}
            for _date in [date_range_7_days,date_range_75_and_7_days]:
                df = pd.DataFrame(columns=["日期","大类排名","广告花费"])
                for _date_1 in _date:
                    df.loc[len(df)] = [_date_1,feishudata[_data][4],feishudata[_data][3]]
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

                df['大类排名'] = df['大类排名'].apply(lambda x : int(re.findall("\d+", str(x))[0]) if re.findall("\d+", str(x)) else 0)
                df['广告花费'] = -df['广告花费'] / 7
                # 预测 C:\Project\Zlwl\PMC\static\msku_fiels_model
                loaded_model = joblib.load(f'C:\\Project\\Zlwl\\PMC\\static\\msku_fiels_model\\{pkl_name}.pkl')
                # 提取特征列
                X = df.drop(columns=['日期'])
                # 将特征数据转换为 DMatrix 格式
                dmatrix_X = xgb.DMatrix(X)
                # 使用加载的模型进行预测
                y_pred = loaded_model.predict(dmatrix_X)
                # 将预测结果添加到 DataFrame 中
                df['预测销量'] = y_pred
                sum_sala = df['预测销量'].sum()
                # 将数字列转换为字符串类型
                string_series = df['预测销量'].astype(str)
                # 使用 transform 和 join 方法进行拼接
                joined_string = ','.join(string_series)
                if ifnum == 0:
                    fields.update({
                        "预测下周销量":joined_string,
                        "预测下周销量(统计)":math.ceil(sum_sala)
                    })
                else:
                    fields.update({
                        "预测75天后(一周)销量":joined_string,
                        "预测75天后(一周统计)销量":math.ceil(sum_sala)
                    })
                ifnum += 1
            update_data_list.append({
                "record_id":_data,
                "fields": fields
            }) 
        if len(update_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data}
                feishuapi().__postUpdatesDatas__(app_token = 'KVZ9bIrm9azOpqseGx3cIkRfn4f', table_id = 'tblzV27KDQw1t96z', payload_dict = payload_dict)