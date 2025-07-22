from django.shortcuts import render
import json
from django.http import HttpResponse
import os
from django.views.decorators.csrf import csrf_exempt
import threading

def Calculate(request, param1, param2, param3, param4):
    current_dir = os.getcwd()  # 返回当前工作目录的绝对路径
    # 方法 1：使用 json.load() 直接读取文件
    with open(os.path.join(current_dir,"Calculator\status\output.json"), 'r', encoding='utf-8') as f:
        data = json.load(f)  # 返回字典（dict）或列表（list）
    # 调用外部API获取数据
    if param1+param2 not in data:
        context = {
            'param1': param1,
            'param2': param2,
        }
        return render(request, 'Calculator/AsinPricing404.html', context)
    api_data = data[param1+param2]
    # 准备初始数据（从API获取或使用默认值）
    initial_data = {
        'advertising_cost_ratio': api_data.get('advertising_cost_ratio', 0.0),
        'refund_promotion_fee_ratio': api_data.get('refund_promotion_fee_ratio', 0.0),
        'commission_fee_ratio': api_data.get('commission_fee_ratio', 0.0),
        'subscription_fee_ratio': api_data.get('subscription_fee_ratio', 0.0),
        'coupon_fee_ratio': api_data.get('coupon_fee_ratio', 0.0),
        'second_kill_cost_ratio': api_data.get('second_kill_cost_ratio', 0.0),
        'FBA_storage_fees_are_lower_than': api_data.get('FBA_storage_fees_are_lower_than', 0.0),
        'other_fees_included': api_data.get('other_fees_included', 0.0),
        'cash_expense_ratio': api_data.get('cash_expense_ratio', 0.0),
        'removal_fee': api_data.get('removal_fee', 0.0),
        'operating_overhead_allocation_ratio': api_data.get('operating_overhead_allocation_ratio', 0.0),
        'purchase_unit_price': api_data.get('purchase_unit_price', 0.0),
        'actual_weight': api_data.get('actual_weight', 0.0),
        'average_price_for_the_first_leg': api_data.get('average_price_for_the_first_leg', 0.0),
        'last_mile_fee': api_data.get('last_mile_fee', 0.0),
        'price': api_data.get('price', 0.0),
        'exchange_rate': api_data.get('exchange_rate', 0.0),
        'vat': api_data.get('vat', 0.0)
    }
    # 将完整API数据转换为JSON字符串
    api_data_json = json.dumps(api_data)
    context = {
        'param1': param1,
        'param2': param2,
        'param3': param3,
        'param4': param4,
        'initial_data': initial_data,
        'api_data_json': api_data_json  # 添加完整的API数据JSON
    }
    return render(request, 'Calculator/AsinPricing.html', context)