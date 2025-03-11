# your_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('example/', views.example_view, name='example'),
    path('pmc_cgdata/', views.pmc_cgdata, name='pmc_cgdata'),
    path('pmc_bhdata/', views.pmc_bhdata, name='pmc_bhdata'),
    path('pmc_aimodel/', views.pmc_aimodel, name='pmc_aimodel'),
    path('pmc_warehouse/', views.pmc_warehouse, name='pmc_warehouse')
]