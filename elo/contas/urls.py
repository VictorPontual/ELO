from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    UserLoginView, UserCadastroView,
    lista_pesquisadores, editar_pesquisador, registro_acoes,
)

urlpatterns = [
    path('', UserLoginView.as_view(), name='login'),
    path('cadastro/', UserCadastroView.as_view(), name='cadastro'),
    path('pesquisadores/', lista_pesquisadores, name='lista_pesquisadores'),
    path('pesquisadores/<int:pk>/editar/', editar_pesquisador, name='editar_pesquisador'),
    path('registro-acoes/', registro_acoes, name='registro_acoes'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
