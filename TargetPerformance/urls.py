# your_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('example/', views.example_view, name='example'),
    path('amazon_partASIN/', views.amazon_partASIN, name='amazon_partASIN'),
    path('amazon_asin/', views.amazon_asin, name='amazon_asin'),
    path('waller_target/', views.waller_target, name='waller_target'),
    path('waller_wfs/', views.waller_wfs, name='waller_wfs'),
]