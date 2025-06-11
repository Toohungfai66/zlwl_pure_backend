# your_app/views.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .code.TikTok import tiktok
import threading

@csrf_exempt
def Order_Management(request):
    thread = threading.Thread(target=tiktok().__ordermanagement__)
    # 启动线程
    thread.start()
    # 主函数继续执行，无需等待线程执行完毕
    return HttpResponse("请等待几分钟!")