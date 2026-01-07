from django.urls import path
from .views import UserLoginView, UserCadastroView

urlpatterns = [
    path('', UserLoginView.as_view(), name='login'),
    path('cadastro/', UserCadastroView.as_view(), name='cadastro'),
]
