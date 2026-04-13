from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_projetos, name='lista_projetos'),
    path('cadastro/', views.cadastro_projeto, name='cadastro_projeto'),
    path('editar/<int:projeto_id>/', views.editar_projeto, name='editar_projeto'),
    path('editar/<int:projeto_id>/adicionar-pesquisador/', views.adicionar_pesquisador, name='adicionar_pesquisador'),
    path('editar/<int:projeto_id>/remover-pesquisador/<int:participacao_id>/', views.remover_pesquisador, name='remover_pesquisador'),
    path('ajax/criar-unidade/', views.criar_unidade_ajax, name='criar_unidade_ajax'),
    path('ajax/criar-classificacao/', views.criar_classificacao_ajax, name='criar_classificacao_ajax'),
    path('ajax/criar-tipo-pesquisa/', views.criar_tipo_pesquisa_ajax, name='criar_tipo_pesquisa_ajax'),
    path('ajax/criar-especialidade/', views.criar_especialidade_ajax, name='criar_especialidade_ajax'),
]
