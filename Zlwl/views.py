# myproject/views.py
from django.http import HttpResponse
from .code.project_id_update import project_id_update_class
def Project_id(request):
    project_id_update_class().project_feishu()
    return HttpResponse("完成!")