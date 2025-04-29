from .FeiShuAPI import feishuapi
# from .LingXingAPI import lingxingapi
from datetime import datetime, timedelta  
import os,json,joblib,requests
import pandas as pd
from datetime import datetime, timedelta
import xgboost as xgb

class cg_aipredit:

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
                    "MSKU",
                    "父ASIN",
                    "ASIN",
                    "周期(第一周)",
                    "周期(第二周)",
                    "周期(第三周)",
                    "周期(第四周)",
                    "周期(第五周)",
                    "周期(第六周)",
                    "周期(第七周)",
                    "周期(第八周)",
                    "周期(第九周)",
                    "周期(第十周)"
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
        return feishu_datas

    def main(self):
        # 获取采购单数据,得到MSKU与父ASIN与ASIN和预测日期以及行id
        FeishuReult = self.FEISHU_FBA_DICT()
        update_data_list = []
        if_list = {}
        # 匹配对应模型，进行预测
        for _data in FeishuReult:
            if "MSKU" in _data["fields"] and "父ASIN" in _data["fields"] and "ASIN" in _data["fields"]:
                pkl_name = _data["fields"]["MSKU"]['value'][0]['text'] + "_" + _data["fields"]["父ASIN"]['value'][0]['text'] + "_" + _data["fields"]["ASIN"]['value'][0]['text']
                pkl_name = str(pkl_name).replace('/', 'or')
                if pkl_name + ".pkl" not in os.listdir("C:\\Project\\Zlwl\\PMC\\static\\msku_fiels_model"):
                    continue
                if pkl_name in if_list:
                    update_data_list.append({
                        "record_id":_data["record_id"],
                        "fields": if_list[pkl_name]
                    }) 
                    continue
                fields = {}
                for _data_1 in ["周期(第一周)","周期(第二周)","周期(第三周)","周期(第四周)","周期(第五周)","周期(第六周)","周期(第七周)","周期(第八周)","周期(第九周)","周期(第十周)"]:
                    # 输入的日期范围字符串
                    date_range_str = _data["fields"][_data_1]['value'][0]['text']

                    # 分割日期范围字符串为起始日期和结束日期
                    start_str, end_str = date_range_str.split('-')

                    # 将字符串转换为 datetime 对象
                    start_date = datetime.strptime(start_str, "%Y/%m/%d")
                    end_date = datetime.strptime(end_str, "%Y/%m/%d")

                    # 生成日期列表
                    date_list = []
                    current_date = start_date
                    while current_date <= end_date:
                        date_list.append(current_date.strftime("%Y-%m-%d"))
                        current_date += timedelta(days=1)

                    # 创建 pandas DataFrame
                    df = pd.DataFrame(date_list, columns=['日期'])
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
                    fields[_data_1.replace("周期","预测销量")] = float(sum_sala)
                if_list.update({pkl_name:fields})
                update_data_list.append({
                    "record_id":_data["record_id"],
                    "fields": fields
                }) 
        if len(update_data_list) != 0:
            # 以500为划分，更新回飞书表格，正常的更新
            for _data in [update_data_list[i:i + 500] for i in range(0, len(update_data_list), 500)]:
                payload_dict = {"records":_data}
                feishuapi().__postUpdatesDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblsiC3jAdIqbbfG', payload_dict = payload_dict)