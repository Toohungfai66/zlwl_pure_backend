from .CG_OrderPurchase import cg_orderPurchase
from .CG_PlanPurchase import cg_planpurchase
from .CG_SupplierLayout import cg_supplierlayout
from .Warehouse import warehouse
from .BH_ProductPerformance import bh_productperformance
from .BH_SalesStatistics import bh_salesstatistics
from .BH_Stockupplan import bh_stockupplan
from .BH_SalesForecast import salesforecast
from .AI_ModelDataRequests_CG import ai_modeldatarequests_cg
from .AI_ModelDataRequests_BH import ai_modeldatarequests_bh
from .ModelTrain_CG import modeltrain_cg
from .ModelTrain_BH import modeltrain_bh
from .FeiShuAPI import feishuapi
from .BH_Getlisting import getlisting
from .CG_AIpredit import cg_aipredit
from .CG_Supplier import cg_supplier
from .Cost_based_pricing import cost_based_pricing
from .Temu_Warehouse import Wdtwarehouse
from .CW_AasinPrice import cw_asinprice
import json
class pmc:
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
    
    def __CGdata__(self):
        for _data in self.data:
            if _data == "亚马逊PMC采购计划":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            cg_planpurchase().main()
            cg_supplierlayout().main()
            cg_orderPurchase().main()
            cg_supplier().main()
            cg_aipredit().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)

    def __CG_orderPurchase__(self):
        for _data in self.data:
            if _data == "亚马逊PMC采购计划-采购单":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            cg_orderPurchase().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)

    def __CW_CostBasedPricing__(self):
        for _data in self.data:
            if _data == "财务PMC成本定价":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            getlisting().main(project = "cw")
            cost_based_pricing().main()
            cw_asinprice().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)

    def __Weekly_Meeting__(self):
        for _data in self.data:
            if _data == "亚马逊周会数据":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            bh_productperformance().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)
        
    def __BHdata__(self):
        for _data in self.data:
            if _data == "亚马逊PMC备货计划":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            getlisting().main(project = "bh")
            bh_salesstatistics().main()
            bh_productperformance().main()
            salesforecast().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)

    def __AImodel__(self):
        for _data in self.data:
            if _data == "AI自主学习模型":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            ai_modeldatarequests_cg().main()
            modeltrain_cg().main()
            ai_modeldatarequests_bh().main()
            modeltrain_bh().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)

    def __Warehouse__(self):
        for _data in self.data:
            if _data == "领星库存明细":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            warehouse().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)

    def __Wdtkcdata__(self):
        for _data in self.data:
            if _data == "旺店通库存明细":
                self.record_id = self.data[_data]
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = {"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行中"}}]})
        try:
            Wdtwarehouse().main()
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行成功"}}]})
        except:
            self.payload_dict.update({"records":[{"record_id":self.record_id,"fields":{"程序运行状态":"程序运行失败"}}]})
        feishuapi().__postUpdatesDatas__(app_token = self.app_token, table_id = self.table_id, payload_dict = self.payload_dict)