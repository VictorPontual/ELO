from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('mais-indicadores/', views.mais_indicadores, name='dashboard_mais'),
    path('tempo-por-etapa/', views.tempo_por_etapa, name='dashboard_tempo'),
    path('financeiro/', views.financeiro, name='dashboard_financeiro'),
    path('relatorios/', views.relatorios, name='dashboard_relatorios'),
]
