from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .models import Pesquisador

# Create your views here.

class UserLoginView(LoginView):
    template_name = 'contas/login.html'
    success_url = reverse_lazy('home') # Defina para onde redirecionar após o login