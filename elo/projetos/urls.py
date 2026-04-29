from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_projetos, name='lista_projetos'),
    path('cadastro/', views.cadastro_projeto, name='cadastro_projeto'),
    path('editar/<int:projeto_id>/', views.editar_projeto, name='editar_projeto'),
    path('editar/<int:projeto_id>/adicionar-pesquisador/', views.adicionar_pesquisador, name='adicionar_pesquisador'),
    path('editar/<int:projeto_id>/remover-pesquisador/<int:participacao_id>/', views.remover_pesquisador, name='remover_pesquisador'),
    path('editar/<int:projeto_id>/adicionar-unidade/', views.adicionar_unidade, name='adicionar_unidade'),
    path('editar/<int:projeto_id>/remover-unidade/<int:envolve_id>/', views.remover_unidade, name='remover_unidade'),
    path('editar/<int:projeto_id>/adicionar-hospital/', views.adicionar_hospital, name='adicionar_hospital'),
    path('editar/<int:projeto_id>/remover-hospital/<int:parceria_id>/', views.remover_hospital, name='remover_hospital'),
    path('ajax/criar-unidade/', views.criar_unidade_ajax, name='criar_unidade_ajax'),
    path('ajax/criar-hospital/', views.criar_hospital_ajax, name='criar_hospital_ajax'),
    path('ajax/criar-classificacao/', views.criar_classificacao_ajax, name='criar_classificacao_ajax'),
    path('ajax/criar-tipo-pesquisa/', views.criar_tipo_pesquisa_ajax, name='criar_tipo_pesquisa_ajax'),
    path('ajax/criar-linha-pesquisa/', views.criar_linha_pesquisa_ajax, name='criar_linha_pesquisa_ajax'),
    path('ajax/criar-especialidade/', views.criar_especialidade_ajax, name='criar_especialidade_ajax'),
    path('ajax/criar-instituicao/', views.criar_instituicao_ajax, name='criar_instituicao_ajax'),
    path('ajax/criar-vinculo/', views.criar_vinculo_ajax, name='criar_vinculo_ajax'),
    path('ajax/criar-funcao/', views.criar_funcao_ajax, name='criar_funcao_ajax'),
]
