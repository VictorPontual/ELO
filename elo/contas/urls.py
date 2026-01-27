from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import UserLoginView, UserCadastroView

urlpatterns = [
    path('', UserLoginView.as_view(), name='login'),
    path('cadastro/', UserCadastroView.as_view(), name='cadastro'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
