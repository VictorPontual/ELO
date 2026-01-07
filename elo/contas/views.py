from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django import forms
from .models import Pesquisador

# Create your views here.

class UserLoginView(LoginView):
    template_name = 'contas/login.html'
    success_url = reverse_lazy('home')

class PesquisadorForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Nome de usuário')
    first_name = forms.CharField(max_length=150, label='Nome')
    last_name = forms.CharField(max_length=150, label='Sobrenome')
    email = forms.EmailField(label='E-mail')
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirme a senha', widget=forms.PasswordInput)
    
    class Meta:
        model = Pesquisador
        fields = ['formacao', 'celular']
        labels = {
            'formacao': 'Formação',
            'celular': 'Celular',
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas não correspondem')
        return password2
    
    def save(self, commit=True):
        pesquisador = super().save(commit=False)
        # Criar usuário do Django para autenticação
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        pesquisador.user = user
        if commit:
            pesquisador.save()
        return pesquisador

class UserCadastroView(CreateView):
    form_class = PesquisadorForm
    template_name = 'contas/cadastro.html'
    success_url = reverse_lazy('login')