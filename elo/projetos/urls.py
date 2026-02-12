from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_projetos, name='lista_projetos'),
    path('cadastro/', views.cadastro_projeto, name='cadastro_projeto'),
]
