from .CG_InventoryDetails import cg_inventorydetails
from .CG_OrderPurchase import cg_orderPurchase
from .CG_PlanPurchase import cg_planpurchase
from .CG_SupplierLayout import cg_supplierlayout
from .BH_BD import bh_bd
from .BH_Procurement import bh_procurement
from .BH_ProductPerformance import bh_productperformance
from .BH_SalesStatistics import bh_salesstatistics
from .BH_Stockupplan import bh_stockupplan
from .Sales_forecast import salesforecast
from .AI_ModelDataRequests import ai_modeldatarequests
from .ModelTrain2 import modeltrain
from .FeiShuAPI import feishuapi
import json
class pmc:
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
    
    def __CGdata__(self):
        for _data in self.data:
            if _data == "亚马逊PMC采购计划":
                self.record_id = self.data[_data]
        try:
            cg_planpurchase().main()
            cg_supplierlayout().main()
            cg_inventorydetails().main()
            cg_orderPurchase().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)

    def __BHdata__(self):
        for _data in self.data:
            if _data == "亚马逊PMC备货计划":
                self.record_id = self.data[_data]
        print("1")
        bh_stockupplan().main()
        print("2")
        bh_procurement().main()
        print("3")
        bh_bd().main()
        print("4")
        bh_productperformance().main()
        print("5")
        salesforecast().main()
        print("6")
        bh_salesstatistics().main()
        print("7")
        self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        # self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)

    def __AImodel__(self):
        for _data in self.data:
            if _data == "AI自主学习模型":
                self.record_id = self.data[_data]
        try:
            ai_modeldatarequests().main()
            modeltrain().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)