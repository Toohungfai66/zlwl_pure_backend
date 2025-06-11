from .Amazon_Target_Performance_PartASIN import amazon_target_performance_partASIN
from .Amazon_Target_Performance_PartASIN_NewProduct import amazon_target_performance_partASIN_newproduct
from .Clean_up_regularly import clean_up_regularly
from .Amazon_Target_Performance_ASIN import amazon_target_performance_asin
from .Waller_Target_Performance import waller_target_performance
from .WFS import wfs
from .FeiShuAPI import feishuapi
import json
class target_Performance:

    def __init__(self):
        self.app_token = "Krz3bhiFoaw8Ans8i1YchYcfnDc"
        self.table_id = "tblKshONitaIxTbI"
        file_path = "C:\Project\Zlwl\Zlwl\static\project_id.json"
        self.payload_dict = {}
        self.record_id = ""
        # 以只读模式打开文件，并指定编码为 utf-8
        with open(file_path, 'r', encoding='utf-8') as file:
            # 使用 json.load() 方法将文件内容解析为 Python 字典
            self.data = json.load(file)
    def __partasin__(self):
        for _data in self.data:
            if _data == "亚马逊目标业绩-父ASIN":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            amazon_target_performance_partASIN().main()
            amazon_target_performance_partASIN_newproduct().main()
            clean_up_regularly().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)
    def __asin__(self):
        for _data in self.data:
            if _data == "亚马逊目标业绩-子ASIN":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            amazon_target_performance_asin().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)

    def __waller__(self):
        for _data in self.data:
            if _data == "沃尔玛目标业绩":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            waller_target_performance().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)

    def __wfs__(self):
        for _data in self.data:
            if _data == "沃尔玛WFS库存更新":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            wfs().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)