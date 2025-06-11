import json
from .FeiShuAPI import feishuapi
from .Order_Management import order_management
class tiktok:
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
    def __ordermanagement__(self):
        for _data in self.data:
            if _data == "TIKTOK订单管理":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            order_management().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        print(self.payload_dict)
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)