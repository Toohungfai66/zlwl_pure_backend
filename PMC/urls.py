# your_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('example/', views.example_view, name='example'),
    path('pmc_cgdata/', views.pmc_cgdata, name='pmc_cgdata'),
    path('pmc_bhdata/', views.pmc_bhdata, name='pmc_bhdata'),
    path('pmc_aimodel/', views.pmc_aimodel, name='pmc_aimodel'),
    path('pmc_warehouse/', views.pmc_warehouse, name='pmc_warehouse'),
    path('cg_orderpurchase/', views.cg_orderpurchase, name='cg_orderpurchase'),
    path('cw_costbasedpricing/', views.cw_costbasedpricing, name='cw_costbasedpricing'),
    path('wdt_kcdata/', views.wdtkcdata, name='wdtkcdata'),
    path('weekly_meeting/', views.weekly_meeting, name='weekly_meeting'),
]