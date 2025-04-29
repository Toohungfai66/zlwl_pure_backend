from .FeiShuAPI import feishuapi
from .LingXingRPA import lingxingrpa
import requests
import json
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os
from urllib.parse import unquote_plus
import pandas as pd

class warehouse:

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

    def FEISHU_FBA_DICT(self,app_token, table_id, project_name = "") -> dict:
        page_token = ''
        has_more = True
        feishu_datas = []
        if project_name == "QC":
            field_names = ["FNSKU"]
        elif project_name == "CG":
            field_names = ["品名"]
        elif project_name == "BDWH":
            field_names = ["SKU","店铺","国家","FNSKU","MSKU","SPU","品名","款名","分类","品牌","仓库名","具体负责人",
                           "0-7天库龄预警","8-15天库龄预警","15天库龄以上(公用量)","可用量","货值","采购单价"]
        elif project_name == "FBA":
            field_names = ["SKU","店铺","国家","FNSKU","MSKU","SPU","品名","款名","分类","品牌","仓库名","具体负责人",
                           "实际在途数量(FBA)","实际在途金额(FBA)","0-60天库龄数量(FBA)","0-60天库龄金额(FBA)","61-90天库龄数量(FBA)","61-90天库龄金额(FBA)",
                           "91-180天库龄数量(FBA)","91-180天库龄金额(FBA)","181天及以上库龄数量(FBA)","181天及以上库龄金额(FBA)","可用库存数量","可用库存金额"]
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
            response = self.get_bitable_datas(app_token = app_token, table_id = table_id, page_token = page_token, filter_condition=filter_condition, page_size=500)
            if response['code'] == 0:
                feishu_datas.extend(response['data']['items'])
                has_more = response['data']['has_more']
                if has_more == False:
                    break
                page_token = response['data']['page_token']
            else:
                raise Exception(response['msg'])
        if project_name == "BDHW" or project_name == "FBA":
            result = {}
            for feishu_data in feishu_datas:
                try:
                    SKU = feishu_data["fields"]["SKU"][0]["text"]
                except:
                    SKU = ""
                try:
                    DP = feishu_data["fields"]["店铺"][0]["text"]
                except:
                    DP = ""
                try:
                    GJ = feishu_data["fields"]["国家"][0]["text"]
                except:
                    GJ = ""
                try:
                    FNSKU = feishu_data["fields"]["FNSKU"][0]["text"]
                except:
                    FNSKU = ""
                try:
                    MSKU = feishu_data["fields"]["MSKU"][0]["text"]
                except:
                    MSKU = ""
                try:
                    SPU = feishu_data["fields"]["SPU"][0]["text"]
                except:
                    SPU = ""
                try:
                    PM = feishu_data["fields"]["品名"][0]["text"]
                except:
                    PM = ""
                try:
                    KM = feishu_data["fields"]["款名"][0]["text"]
                except:
                    KM = ""
                try:
                    FL = feishu_data["fields"]["分类"][0]["text"]
                except:
                    FL = ""
                try:
                    PP = feishu_data["fields"]["品牌"][0]["text"]
                except:
                    PP = ""
                try:
                    CKM = feishu_data["fields"]["仓库名"]
                except:
                    CKM = ""
                try:
                    JTFZR = feishu_data["fields"]["具体负责人"][0]["text"]
                except:
                    JTFZR = ""
                jcsj = {
                    "SKU":SKU,
                    "店铺":DP,
                    "国家":GJ,
                    "FNSKU":FNSKU,
                    "MSKU":MSKU,
                    "SPU":SPU,
                    "品名":PM,
                    "款名":KM,
                    "分类":FL,
                    "品牌":PP,
                    "仓库名":CKM,
                    "具体负责人":JTFZR
                }
                if project_name == "BDHW":
                    jcsj.update({
                        "0-7天库龄预警":feishu_data["fields"]["0-7天库龄预警"],
                        "0-7天库龄金额":feishu_data["fields"]["0-7天库龄预警"] * feishu_data["fields"]["采购单价"],
                        "8-15天库龄预警":feishu_data["fields"]["8-15天库龄预警"],
                        "8-15天库龄金额":feishu_data["fields"]["8-15天库龄预警"] * feishu_data["fields"]["采购单价"],
                        "15天库龄以上(公用量)":feishu_data["fields"]["15天库龄以上(公用量)"],
                        "15天库龄以上金额(公用量)":feishu_data["fields"]["15天库龄以上(公用量)"] * feishu_data["fields"]["采购单价"],
                        "可用量":feishu_data["fields"]["可用量"],
                        "货值":feishu_data["fields"]["货值"]
                        })
                else:
                    jcsj.update({
                        "可用库存数量":feishu_data["fields"]["可用库存数量"],
                        "可用库存金额":feishu_data["fields"]["可用库存金额"],
                        "实际在途数量(FBA)":feishu_data["fields"]["实际在途数量(FBA)"],
                        "实际在途金额(FBA)":feishu_data["fields"]["实际在途金额(FBA)"],
                        "0-60天库龄数量(FBA)":feishu_data["fields"]["0-60天库龄数量(FBA)"],
                        "0-60天库龄金额(FBA)":feishu_data["fields"]["0-60天库龄金额(FBA)"],
                        "61-90天库龄数量(FBA)":feishu_data["fields"]["61-90天库龄数量(FBA)"],
                        "61-90天库龄金额(FBA)":feishu_data["fields"]["61-90天库龄金额(FBA)"],
                        "91-180天库龄数量(FBA)":feishu_data["fields"]["91-180天库龄数量(FBA)"],
                        "91-180天库龄金额(FBA)":feishu_data["fields"]["91-180天库龄金额(FBA)"],
                        "181天及以上库龄数量(FBA)":feishu_data["fields"]["181天及以上库龄数量(FBA)"],
                        "181天及以上库龄金额(FBA)":feishu_data["fields"]["181天及以上库龄金额(FBA)"]
                        })
                result[feishu_data["record_id"]] = jcsj
        else:
            result = []
            for feishu_data in feishu_datas:
                result.append(feishu_data["record_id"])
        return result
    
    # 采购公用仓库存
    def project_CG(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        # 初始化WebDriver
        driver = webdriver.Chrome(options=options)
        # 打开网页
        driver.get('https://erp.lingxing.com/login')
        # 登录模块
        # 使用设置的账号和密码填充输入框
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/form/div[1]/div/div/input').send_keys("xiaodu66")
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/form/div[2]/div/div/input').send_keys("D123456789")
        # 提交表单
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/form/div[4]/div/button').click()
        time.sleep(10)
        for cookie in driver.get_cookies():
            if cookie["name"] == 'authToken':
                result_cookie = unquote_plus(cookie['value'])
        cookies = unquote(result_cookie)
        LingxingBDKCResult = lingxingrpa(cookies=cookies).__getBDKCdata__(wid_list="6512,14508,8356,14437,11459,11458,12136,14548,12098,4508,14119,13301,14125,13296,14121,13297,14127,13294,14120,13293,14123,13300,14126,13292,14124,13295,14128,13298,14122,13299,8349,10040,10834,13086,6927,7111,8350,9485,7757,13609,13610,13611,6925,13095,6928,11214,12066,6511,8353")
        LingxingHWKCResult = lingxingrpa(cookies=cookies).__getBDKCdata__(wid_list="11820,11301,7513,12137,12503,12099,12523,7056,13446,7216,8982,14314,13447,7038,8207,12758,7747,7144,8981,9486,6589,9173,9456,7215,7254,7042,7041,7212,7040")
        LingxingFBAResult = lingxingrpa(cookies=cookies).__getFBAKCdata__()
        driver.close()
        driver.quit()
        # 本地仓库存
        insert_data_list = []
        for _data in LingxingBDKCResult:
            pay_dict = {
                "品名":LingxingBDKCResult[_data]["product_name"],
                "仓库名":LingxingBDKCResult[_data]["wh_name"],
                "0-7天库龄预警":LingxingBDKCResult[_data]["yj_one"],
                "8-15天库龄预警":LingxingBDKCResult[_data]["yj_two"],
                "15天库龄以上(公用量)":LingxingBDKCResult[_data]["gy"],
                "FNSKU":LingxingBDKCResult[_data]["fnsku"],
                "MSKU":LingxingBDKCResult[_data]["msku"],
                "SKU":LingxingBDKCResult[_data]["sku"],
                "可用量":LingxingBDKCResult[_data]["good_num"],
                "采购单价":LingxingBDKCResult[_data]["purchase_price"],
                "货值":LingxingBDKCResult[_data]["stock_cost"],
                "店铺":LingxingBDKCResult[_data]["store_name_list"],
                "SPU":LingxingBDKCResult[_data]["spu"],
                "款名":LingxingBDKCResult[_data]["spu_name"],
                "分类":LingxingBDKCResult[_data]["category_name"],
                "国家":LingxingBDKCResult[_data]["country"],
                "品牌":LingxingBDKCResult[_data]["brand_name"]
            }
            JTFZR = ""
            for _data_1 in LingxingBDKCResult[_data]["principal_name_list"]:
                JTFZR = JTFZR + _data_1 + ","
            pay_dict.update({"具体负责人":JTFZR[:-1]})
            insert_data_list.append({"fields":pay_dict})
        delete_data_list = self.FEISHU_FBA_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tbleZ1v87gYaCB7G",project_name="CG")
        for _data in [delete_data_list[i:i + 500] for i in range(0, len(delete_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbleZ1v87gYaCB7G', payload_dict = payload_dict)
        # 以500为划分，更新回飞书表格，正常的更新
        for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbleZ1v87gYaCB7G', payload_dict = payload_dict)
        
        # 海外仓库存
        insert_data_list = []
        for _data in LingxingHWKCResult:
            pay_dict = {
                "品名":LingxingHWKCResult[_data]["product_name"],
                "仓库名":LingxingHWKCResult[_data]["wh_name"],
                "0-7天库龄预警":LingxingHWKCResult[_data]["yj_one"],
                "8-15天库龄预警":LingxingHWKCResult[_data]["yj_two"],
                "15天库龄以上(公用量)":LingxingHWKCResult[_data]["gy"],
                "FNSKU":LingxingHWKCResult[_data]["fnsku"],
                "SKU":LingxingHWKCResult[_data]["sku"],
                "MSKU":LingxingHWKCResult[_data]["msku"],
                "可用量":LingxingHWKCResult[_data]["good_num"],
                "采购单价":LingxingHWKCResult[_data]["purchase_price"],
                "货值":LingxingHWKCResult[_data]["stock_cost"],
                "店铺":LingxingHWKCResult[_data]["store_name_list"],
                "SPU":LingxingHWKCResult[_data]["spu"],
                "款名":LingxingHWKCResult[_data]["spu_name"],
                "分类":LingxingHWKCResult[_data]["category_name"],
                "国家":LingxingHWKCResult[_data]["country"],
                "品牌":LingxingHWKCResult[_data]["brand_name"]
            }
            JTFZR = ""
            for _data_1 in LingxingHWKCResult[_data]["principal_name_list"]:
                JTFZR = JTFZR + _data_1 + ","
            pay_dict.update({"具体负责人":JTFZR[:-1]})
            insert_data_list.append({"fields":pay_dict})
        delete_data_list = self.FEISHU_FBA_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tbllrmE3JEIPxhnC",project_name="CG")
        for _data in [delete_data_list[i:i + 500] for i in range(0, len(delete_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbllrmE3JEIPxhnC', payload_dict = payload_dict)
        # 以500为划分，更新回飞书表格，正常的更新
        for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbllrmE3JEIPxhnC', payload_dict = payload_dict)

        # FBA库存明细
        insert_data_list = []
        for _data in LingxingFBAResult:
            pay_dict = {
                    "FNSKU":LingxingFBAResult[_data]["fnsku"],
                    "仓库名":LingxingFBAResult[_data]["name"],
                    "父ASIN":LingxingFBAResult[_data]["parent_asin_real"],
                    "SKU":LingxingFBAResult[_data]["sku"],
                    "品名":LingxingFBAResult[_data]["product_name"],
                    "ASIN":LingxingFBAResult[_data]["asin"],
                    "SPU":LingxingFBAResult[_data]["spu"],
                    "款名":LingxingFBAResult[_data]["spu_name"],
                    "分类":LingxingFBAResult[_data]["category_text"],
                    "品牌":LingxingFBAResult[_data]["product_brand_text"],
                    "MSKU":LingxingFBAResult[_data]["seller_sku"],
                    "可用库存数量":LingxingFBAResult[_data]["available_total"],
                    "可用库存金额":LingxingFBAResult[_data]["available_total_price"],
                    "总库存数量(FBA)":LingxingFBAResult[_data]["total"],
                    "总库存金额(FBA)":LingxingFBAResult[_data]["total_amount"],
                    "标发在途数量(FBA)":LingxingFBAResult[_data]["afn_inbound_shipped_quantity"],
                    "标发在途金额(FBA)":LingxingFBAResult[_data]["afn_inbound_shipped_quantity_price"],
                    "实际在途数量(FBA)":LingxingFBAResult[_data]["stock_up_num"],
                    "实际在途金额(FBA)":LingxingFBAResult[_data]["stock_up_num_price"],
                    "0-60天库龄数量(FBA)":LingxingFBAResult[_data]["inv_age_0_to_60_days"],
                    "0-60天库龄金额(FBA)":LingxingFBAResult[_data]["inv_age_0_to_60_price"],
                    "61-90天库龄数量(FBA)":LingxingFBAResult[_data]["inv_age_61_to_90_days"],
                    "61-90天库龄金额(FBA)":LingxingFBAResult[_data]["inv_age_61_to_90_price"],
                    "91-180天库龄数量(FBA)":LingxingFBAResult[_data]["inv_age_91_to_180_days"],
                    "91-180天库龄金额(FBA)":LingxingFBAResult[_data]["inv_age_91_to_180_price"],
                    "181天及以上库龄数量(FBA)":LingxingFBAResult[_data]["inv_age_181_plus_days"],
                    "181天及以上库龄金额(FBA)":LingxingFBAResult[_data]["inv_age_181_plus_price"]
            }
            JTFZR = ""
            for _data_1 in LingxingFBAResult[_data]["asin_principal"]:
                JTFZR = JTFZR + _data_1 + ","
            pay_dict.update({"具体负责人":JTFZR[:-1]})
            insert_data_list.append({"fields":pay_dict})
        delete_data_list = self.FEISHU_FBA_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f",table_id="tbl5WaiRhL8hmSb0",project_name="CG")
        for _data in [delete_data_list[i:i + 500] for i in range(0, len(delete_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbl5WaiRhL8hmSb0', payload_dict = payload_dict)
        # 以500为划分，更新回飞书表格，正常的更新
        for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbl5WaiRhL8hmSb0', payload_dict = payload_dict)

    def get_latest_file(self,folder_path):
        latest_file = None
        latest_mtime = 0
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if "全仓明细详情信息" in file:
                    file_path = os.path.join(root, file)
                    mtime = os.path.getmtime(file_path)
                    if mtime > latest_mtime:
                        latest_mtime = mtime
                        latest_file = file_path
        return latest_file
    
# 采购公用仓库存
    def project_QC(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        # 初始化WebDriver
        driver = webdriver.Chrome(options=options)
        # 设置隐式等待时间为10秒
        driver.implicitly_wait(10)
        # 最大化窗口
        driver.maximize_window()
        # 打开网页
        driver.get('https://erp.lingxing.com/login')
        # 登录模块
        # 使用设置的账号和密码填充输入框
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/form/div[1]/div/div/input').send_keys("xiaodu66")
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/form/div[2]/div/div/input').send_keys("D123456789")
        # 提交表单
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/div[2]/form/div[4]/div/button').click()
        # 进入全仓明细
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/ul/li[5]/a').click()
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[2]/div[1]/div[5]/div/a').click()
        # 提示
        try:
            driver.find_element(By.XPATH, '//*[@id="auto-height"]/div/div[2]/span/button').click()
            driver.find_element(By.XPATH, '//*[@id="auto-height"]/div/div[2]/span/button[2]').click()
        except:
            pass
        # 导出数据
        driver.find_element(By.XPATH, '//*[@id="supplyApp"]/div/div[2]/div/div[2]/button').click()
        time.sleep(1)
        driver.find_element(By.XPATH, '//*[@id="supplyApp"]/div/div[4]/div/div[2]/div/div[2]/div[1]/label/span[1]/span').click()
        time.sleep(1)
        driver.find_element(By.XPATH, '//*[@id="supplyApp"]/div/div[4]/div/div[2]/div/div[2]/div[1]/label/span[1]/span').click()
        driver.find_element(By.XPATH, '//*[@id="supplyApp"]/div/div[4]/div/div[2]/div/div[8]/label[3]/span[1]/span').click()
        driver.find_element(By.XPATH, '//*[@id="supplyApp"]/div/div[4]/div/div[3]/div/button[2]/span').click()
        # 下载数据
        WebDriverWait(driver, 600).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.el-button.el-button--ordinary.el-button--mini.is-round[data-auth="auth-button"]'))).click()
        time.sleep(120)
        driver.close()
        driver.quit()
        # 读取数据进行预处理
        excel_path = self.get_latest_file(folder_path="C:\\Users\\duhon\\Downloads")

        # 读取Excel数据
        df = pd.read_excel(
            excel_path,
            sheet_name="sheet1",
            usecols=[
                '品名', 'SKU', '仓库', '店铺', 'FNSKU', 'MSKU', 'ASIN',
                '款名', 'SPU', '品牌', 'Listing负责人', '分类', '0~30库龄数量', '0~30库龄成本',
                '31~60库龄数量', '31~60库龄成本','61~90库龄数量', '61~90库龄成本',
                '91~180库龄数量', '91~180库龄成本',
                '181~270库龄数量', '181~270库龄成本', '271~330库龄数量',
                '271~330库龄成本', '331~365库龄数量', '331~365库龄成本',
                '365以上库龄数量', '365以上库龄成本'
            ],
            dtype={'款名': str, 'SPU': str}  # 处理可能存在的空值列
        ).rename(columns={
            '品名': "商品全称",
            'ASIN': "子ASIN",
            '款名': "商品简称",
            '仓库': "仓库名称",
            '分类':'商品系列',
            'Listing负责人':"具体负责人",
            '61~90库龄数量': "61~90库龄数量（全仓）",
            '61~90库龄成本': "61~90库龄金额（全仓）",
            '91~180库龄数量': "91~180库龄数量（全仓）",
            '91~180库龄成本': "91~180库龄金额（全仓）"
        })  # 空值填充为0

        # 计算复合库龄列
        df['0~60库龄数量（全仓）'] = df.eval('`0~30库龄数量` + `31~60库龄数量`')
        df['0~60库龄金额（全仓）'] = df.eval('`0~30库龄成本` + `31~60库龄成本`')
        df['181以上库龄数量（全仓）'] = df.eval(
            '`181~270库龄数量` + `271~330库龄数量` + `331~365库龄数量` +  `365以上库龄数量`')
        df['181以上库龄金额（全仓）'] = df.eval(
            '`181~270库龄成本` + `271~330库龄成本` + `331~365库龄成本`+  `365以上库龄成本`')
        del df["0~30库龄数量"]
        del df["0~30库龄成本"]
        del df["31~60库龄数量"]
        del df["31~60库龄成本"]
        del df["181~270库龄数量"]
        del df["181~270库龄成本"]
        del df["271~330库龄数量"]
        del df["271~330库龄成本"]
        del df["331~365库龄数量"]
        del df["331~365库龄成本"]
        del df["365以上库龄数量"]
        del df["365以上库龄成本"]
        # 构建数据结构（使用列表推导式）
        insert_data_list = [
            {"fields": row.where(pd.notnull(row), None).to_dict()}  # 处理NaN值
            for _, row in df.iterrows()
        ]
        # 查询飞书数据
        delete_data_list = self.FEISHU_FBA_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f", table_id="tbl1evLX1uVd5TJ3", project_name="QC")
        # 删除原飞书数据
        for _data in [delete_data_list[i:i + 500] for i in range(0, len(delete_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbl1evLX1uVd5TJ3', payload_dict = payload_dict)
        # 插入最新数据
        for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tbl1evLX1uVd5TJ3', payload_dict = payload_dict)

    def project_HB(self):
        BD = self.FEISHU_FBA_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f", table_id="tbleZ1v87gYaCB7G", project_name="BDHW")
        HW = self.FEISHU_FBA_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f", table_id="tbllrmE3JEIPxhnC", project_name="BDHW")
        FBA = self.FEISHU_FBA_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f", table_id="tbl5WaiRhL8hmSb0", project_name="FBA")
        All_data = {}
        All_data.update(BD)
        All_data.update(HW)
        All_data.update(FBA)
        # 合并
        insert_data_list = []
        for _data in All_data:
            pay_dict = {
                "SKU":All_data[_data]["SKU"],
                "店铺":All_data[_data]["店铺"],
                "国家":All_data[_data]["国家"],
                "FNSKU":All_data[_data]["FNSKU"],
                "MSKU":All_data[_data]["MSKU"],
                "SPU":All_data[_data]["SPU"],
                "商品全称":All_data[_data]["品名"],
                "商品简称":All_data[_data]["款名"],
                "商品系列":All_data[_data]["分类"],
                "品牌":All_data[_data]["品牌"],
                "仓库名":All_data[_data]["仓库名"],
                "具体负责人":All_data[_data]["具体负责人"]
            }
            
            if _data in BD or _data in HW:
                pay_dict.update({
                    "FBA在库数量":0,
                    "FBA在库金额":0,
                    "FBA在途数量":0,
                    "FBA在途金额":0,
                    "0-60天库龄数量(FBA)":0,
                    "0-60天库龄金额(FBA)":0,
                    "61-90天库龄数量(FBA)":0,
                    "61-90天库龄金额(FBA)":0,
                    "91-180天库龄数量(FBA)":0,
                    "91-180天库龄金额(FBA)":0,
                    "181天及以上库龄数量(FBA)":0,
                    "181天及以上库龄金额(FBA)":0
                })
                if _data in BD:
                    pay_dict.update({
                        "海外仓在库数量":0,
                        "海外仓在库金额":0,
                    })
                else:
                    pay_dict.update({
                        "本地仓在库数量":0,
                        "本地仓在库金额":0
                    })
            else:
                pay_dict.update({
                    "0-7天库龄数量（本地仓海外仓预警）":0,
                    "0-7天库龄金额（本地仓海外仓预警）":0,
                    "8-14天库龄数量（本地仓海外仓预警）":0,
                    "8-14天库龄金额（本地仓海外仓预警）":0,
                    "15天以上库龄数量（本地仓海外仓可转公用）":0,
                    "15天以上库龄金额（本地仓海外仓可转公用）":0,
                    "海外仓在库数量":0,
                    "海外仓在库金额":0,
                    "本地仓在库数量":0,
                    "本地仓在库金额":0
                })
            if _data in BD:
                pay_dict.update({
                    "0-7天库龄数量（本地仓海外仓预警）":All_data[_data]["0-7天库龄预警"],
                    "0-7天库龄金额（本地仓海外仓预警）":All_data[_data]["0-7天库龄金额"],
                    "8-14天库龄数量（本地仓海外仓预警）":All_data[_data]["8-15天库龄预警"],
                    "8-14天库龄金额（本地仓海外仓预警）":All_data[_data]["8-15天库龄金额"],
                    "15天以上库龄数量（本地仓海外仓可转公用）":All_data[_data]["15天库龄以上(公用量)"],
                    "15天以上库龄金额（本地仓海外仓可转公用）":All_data[_data]["15天库龄以上金额(公用量)"],
                    "本地仓在库数量":All_data[_data]["可用量"],
                    "本地仓在库金额":All_data[_data]["货值"]
                })
                pay_dict.update({"仓库区域":"本地仓"})
            elif _data in HW:
                pay_dict.update({
                    "0-7天库龄数量（本地仓海外仓预警）":All_data[_data]["0-7天库龄预警"],
                    "0-7天库龄金额（本地仓海外仓预警）":All_data[_data]["0-7天库龄金额"],
                    "8-14天库龄数量（本地仓海外仓预警）":All_data[_data]["8-15天库龄预警"],
                    "8-14天库龄金额（本地仓海外仓预警）":All_data[_data]["8-15天库龄金额"],
                    "15天以上库龄数量（本地仓海外仓可转公用）":All_data[_data]["15天库龄以上(公用量)"],
                    "15天以上库龄金额（本地仓海外仓可转公用）":All_data[_data]["15天库龄以上金额(公用量)"],
                    "海外仓在库数量":All_data[_data]["可用量"],
                    "海外仓在库金额":All_data[_data]["货值"]
                })
                pay_dict.update({"仓库区域":"海外仓"})
            else:
                pay_dict.update({
                    "FBA在库数量":All_data[_data]["可用库存数量"],
                    "FBA在库金额":All_data[_data]["可用库存金额"],
                    "FBA在途数量":All_data[_data]["实际在途数量(FBA)"],
                    "FBA在途金额":All_data[_data]["实际在途金额(FBA)"],
                    "0-60天库龄数量(FBA)":All_data[_data]["0-60天库龄数量(FBA)"],
                    "0-60天库龄金额(FBA)":All_data[_data]["0-60天库龄数量(FBA)"],
                    "61-90天库龄数量(FBA)":All_data[_data]["61-90天库龄数量(FBA)"],
                    "61-90天库龄金额(FBA)":All_data[_data]["61-90天库龄金额(FBA)"],
                    "91-180天库龄数量(FBA)":All_data[_data]["91-180天库龄数量(FBA)"],
                    "91-180天库龄金额(FBA)":All_data[_data]["91-180天库龄金额(FBA)"],
                    "181天及以上库龄数量(FBA)":All_data[_data]["181天及以上库龄数量(FBA)"],
                    "181天及以上库龄金额(FBA)":All_data[_data]["181天及以上库龄金额(FBA)"]
                })
                pay_dict.update({"仓库区域":"FBA仓"})
            insert_data_list.append({"fields":pay_dict})
        # 查询飞书数据
        delete_data_list = self.FEISHU_FBA_DICT(app_token="TxmobrecbaIyblsh9p8cv3k6n3f", table_id="tblLcwFImaNLcJVc")
        # 删除原飞书数据
        for _data in [delete_data_list[i:i + 500] for i in range(0, len(delete_data_list), 500)]:
            payload_dict = {"records":_data}
            feishuapi().__deleteBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblLcwFImaNLcJVc', payload_dict = payload_dict)
        # 以500为划分，更新回飞书表格，正常的更新
        for _data in [insert_data_list[i:i + 500] for i in range(0, len(insert_data_list), 500)]:
            payload_dict = {"records":_data}
            print(feishuapi().__insertBitableDatas__(app_token = 'TxmobrecbaIyblsh9p8cv3k6n3f', table_id = 'tblLcwFImaNLcJVc', payload_dict = payload_dict))
    def main(self):
        self.project_CG()
        self.project_HB()
        # self.project_QC()