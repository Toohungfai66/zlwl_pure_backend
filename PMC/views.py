# your_app/views.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import threading
from .code.PMC import pmc

@csrf_exempt
def example_view(request):
    print('Request headers:', request.headers)
    print('Request body:', request.body)
    return HttpResponse("这是子应用的示例视图。")

@csrf_exempt
def pmc_cgdata(request): 
    thread = threading.Thread(target=pmc().__CGdata__)
    # 启动线程
    thread.start()
    # 主函数继续执行，无需等待线程执行完毕
    return HttpResponse("请等待几分钟!")

@csrf_exempt
def pmc_bhdata(request):
    thread = threading.Thread(target=pmc().__BHdata__)
    # 启动线程
    thread.start()
    # 主函数继续执行，无需等待线程执行完毕
    return HttpResponse("请等待几分钟!")

@csrf_exempt
def pmc_aimodel(request):
    thread = threading.Thread(target=pmc().__AImodel__)
    # 启动线程
    thread.start()
    # 主函数继续执行，无需等待线程执行完毕
    return HttpResponse("请等待几分钟!")

@csrf_exempt
def pmc_warehouse(request):
    thread = threading.Thread(target=pmc().__Warehouse__)
    # 启动线程
    thread.start()
    # 主函数继续执行，无需等待线程执行完毕
    return HttpResponse("请等待几分钟!")

def cg_orderpurchase(request):
    thread = threading.Thread(target=pmc().__CG_orderPurchase__)
    # 启动线程
    thread.start()
    # 主函数继续执行，无需等待线程执行完毕
    return HttpResponse("请等待几分钟!")