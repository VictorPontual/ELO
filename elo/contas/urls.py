from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    UserLoginView, UserCadastroView,
    meu_cadastro, meus_estudos, novo_projeto, editar_pesquisador,
    registro_acoes, gerenciar_acessos,
)

urlpatterns = [
    path('', UserLoginView.as_view(), name='login'),
    path('cadastro/', UserCadastroView.as_view(), name='cadastro'),
    # A aba Pesquisadores abre na subaba Meu cadastro.
    path('pesquisadores/', meu_cadastro, name='lista_pesquisadores'),
    path('pesquisadores/meus-estudos/', meus_estudos, name='pesquisador_estudos'),
    path('pesquisadores/novo-projeto/', novo_projeto, name='pesquisador_novo_projeto'),
    path('pesquisadores/<int:pk>/editar/', editar_pesquisador, name='editar_pesquisador'),
    path('registro-acoes/', registro_acoes, name='registro_acoes'),
    path('acessos/', gerenciar_acessos, name='gerenciar_acessos'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
