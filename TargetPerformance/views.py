# your_app/views.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .code.Target_Performance import target_Performance
import threading

@csrf_exempt
def example_view(request):
    print('Request headers:', request.headers)
    print('Request body:', request.body)
    return HttpResponse("这是子应用的示例视图。")

@csrf_exempt
def amazon_partASIN(request):
    thread = threading.Thread(target=target_Performance().__partasin__)
    # 启动线程
    thread.start()
    # 主函数继续执行，无需等待线程执行完毕
    return HttpResponse("请等待几分钟!")

@csrf_exempt
def amazon_asin(request):
    thread = threading.Thread(target=target_Performance().__asin__)
    # 启动线程
    thread.start()
    # 主函数继续执行，无需等待线程执行完毕
    return HttpResponse("请等待几分钟!")

@csrf_exempt
def waller_target(request):
    thread = threading.Thread(target=target_Performance().__waller__)
    # 启动线程
    thread.start()
    # 主函数继续执行，无需等待线程执行完毕
    return HttpResponse("请等待几分钟!")

@csrf_exempt
def waller_wfs(request):
    thread = threading.Thread(target=target_Performance().__wfs__)
    # 启动线程
    thread.start()
    # 主函数继续执行，无需等待线程执行完毕
    return HttpResponse("请等待几分钟!")