# your_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('OrderManagement/', views.Order_Management)
]