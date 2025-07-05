# your_app/views.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .code.Walmart import walmart
import threading

@csrf_exempt
def Weekly_Meeting(request):
    thread = threading.Thread(target=walmart().__WeeklyMeeting__)
    # 启动线程
    thread.start()
    # 主函数继续执行，无需等待线程执行完毕
    return HttpResponse("请等待几分钟!")

@csrf_exempt
def Pmc_Bhdata(request):
    thread = threading.Thread(target=walmart().__BHdata__)
    # 启动线程
    thread.start()
    # 主函数继续执行，无需等待线程执行完毕
    return HttpResponse("请等待几分钟!")