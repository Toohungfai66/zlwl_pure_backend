# your_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('calculate/<str:param1>/<str:param2>/<str:param3>/<str:param4>/', 
         views.Calculate, name='Calculate'),
]