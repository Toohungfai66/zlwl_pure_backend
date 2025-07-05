from .FeiShuAPI import feishuapi
from .WeeklyMeeting import weeklymeeting
from .BH_OnlineProducts import bh_onlineproducts
from .BH_SalesForecast import bh_salesforecast
from .BH_SalesStatistics import bh_salesstatistics
import json

class walmart:
    def __init__(self):
        self.app_token = "Krz3bhiFoaw8Ans8i1YchYcfnDc"
        self.table_id = "tblKshONitaIxTbI"
        file_path = "C:\Project\zlwl_pure_backend\Zlwl\static\project_id.json"
        self.payload_dict = {}
        self.record_id = ""
        # 以只读模式打开文件，并指定编码为 utf-8
        with open(file_path, 'r', encoding='utf-8') as file:
            # 使用 json.load() 方法将文件内容解析为 Python 字典
            self.data = json.load(file)

    def __WeeklyMeeting__(self):
        for _data in self.data:
            if _data == "沃尔玛周会数据":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            weeklymeeting().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict) 

    def __BHdata__(self):
        for _data in self.data:
            if _data == "沃尔玛PMC备货计划":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            bh_onlineproducts().main()
            bh_salesstatistics().main()
            # bh_salesforecast().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)