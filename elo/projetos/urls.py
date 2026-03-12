from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_projetos, name='lista_projetos'),
    path('cadastro/', views.cadastro_projeto, name='cadastro_projeto'),
    path('editar/<int:projeto_id>/', views.editar_projeto, name='editar_projeto'),
    path('editar/<int:projeto_id>/adicionar-pesquisador/', views.adicionar_pesquisador, name='adicionar_pesquisador'),
    path('editar/<int:projeto_id>/remover-pesquisador/<int:participacao_id>/', views.remover_pesquisador, name='remover_pesquisador'),
]
