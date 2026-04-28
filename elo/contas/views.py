from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django import forms
from .models import Pesquisador

# Create your views here.


class AdminOnlyAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not (user.is_staff or user.is_superuser):
            raise forms.ValidationError(
                'Acesso permitido apenas para contas administrativas.',
                code='admin_only',
            )

class UserLoginView(LoginView):
    template_name = 'contas/login.html'
    authentication_form = AdminOnlyAuthenticationForm
    success_url = reverse_lazy('home')


class PesquisadorForm(forms.ModelForm):
    nome = forms.CharField(max_length=150, label='Nome')
    celular = forms.CharField(max_length=25, label='Celular', required=False)
    email = forms.EmailField(label='E-mail')
    preferencia_comunicacao_celular = forms.BooleanField(
        label='Preferencia de contato por celular',
        required=False,
    )
    preferencia_comunicacao_email = forms.BooleanField(
        label='Preferencia de contato por e-mail',
        required=False,
    )

    field_order = [
        'nome',
        'celular',
        'preferencia_comunicacao_celular',
        'email',
        'preferencia_comunicacao_email',
    ]
    
    class Meta:
        model = Pesquisador
        fields = [
            'celular',
            'preferencia_comunicacao_celular',
            'preferencia_comunicacao_email',
        ]
        labels = {
            'celular': 'Celular',
            'preferencia_comunicacao_celular': 'Preferencia de contato por celular',
            'preferencia_comunicacao_email': 'Preferencia de contato por e-mail',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ja existe um pesquisador cadastrado com este e-mail.')
        return email

    def _build_unique_username(self, email):
        base = email.split('@')[0][:120] or 'pesquisador'
        candidate = base
        suffix = 1

        while User.objects.filter(username=candidate).exists():
            candidate = f'{base}_{suffix}'
            suffix += 1

        return candidate
    
    def save(self, commit=True):
        pesquisador = super().save(commit=False)
        email = self.cleaned_data['email']
        nome = self.cleaned_data['nome']

        # Cria uma conta tecnica inativa somente para manter integridade do relacionamento.
        user = User.objects.create_user(
            username=self._build_unique_username(email),
            email=email,
            first_name=nome,
            last_name=''
        )
        user.set_unusable_password()
        user.is_active = False
        user.save(update_fields=['password', 'is_active'])

        pesquisador.user = user
        if commit:
            pesquisador.save()
        return pesquisador


class UserCadastroView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    form_class = PesquisadorForm
    template_name = 'contas/cadastro.html'
    success_url = reverse_lazy('cadastro')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'Apenas administradores podem cadastrar pesquisadores.')
        return redirect('lista_projetos')

    def form_valid(self, form):
        messages.success(self.request, 'Pesquisador cadastrado com sucesso.')
        return super().form_valid(form)