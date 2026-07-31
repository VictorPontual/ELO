from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    UserLoginView, UserCadastroView,
    lista_pesquisadores, editar_pesquisador, registro_acoes,
    gerenciar_acessos,
)

urlpatterns = [
    path('', UserLoginView.as_view(), name='login'),
    path('cadastro/', UserCadastroView.as_view(), name='cadastro'),
    path('pesquisadores/', lista_pesquisadores, name='lista_pesquisadores'),
    path('pesquisadores/<int:pk>/editar/', editar_pesquisador, name='editar_pesquisador'),
    path('registro-acoes/', registro_acoes, name='registro_acoes'),
    path('acessos/', gerenciar_acessos, name='gerenciar_acessos'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
