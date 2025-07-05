# your_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('Weekly_Meeting/', views.Weekly_Meeting, name='Weekly_Meeting'),
    path('Pmc_Bhdata/', views.Pmc_Bhdata, name='Pmc_Bhdata'),
]