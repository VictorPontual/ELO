from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django import forms
from .models import Pesquisador, RegistroAcao

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
    ddd = forms.CharField(
        max_length=2,
        label='DDD',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ex.: 61',
            'inputmode': 'numeric',
            'maxlength': '2',
        }),
    )
    celular = forms.CharField(
        max_length=25,
        label='Celular',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ex.: 91234-5678'}),
    )
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
        'ddd',
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

    def clean_ddd(self):
        ddd = (self.cleaned_data.get('ddd') or '').strip()
        if ddd and (not ddd.isdigit() or len(ddd) != 2):
            raise forms.ValidationError('Informe o DDD com 2 dígitos. Ex.: 61.')
        return ddd

    def clean(self):
        cleaned_data = super().clean()
        ddd = (cleaned_data.get('ddd') or '').strip()
        celular = (cleaned_data.get('celular') or '').strip()
        if ddd and not celular:
            self.add_error('celular', 'Informe o número do celular junto com o DDD.')
        return cleaned_data

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

        ddd = (self.cleaned_data.get('ddd') or '').strip()
        celular = (self.cleaned_data.get('celular') or '').strip()
        if ddd and celular:
            pesquisador.celular = f'({ddd}) {celular}'

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


def _separar_ddd_celular(celular):
    """Extrai (ddd, numero) de um celular no formato '(DD) numero'."""
    celular = (celular or '').strip()
    if celular.startswith('(') and ')' in celular:
        ddd = celular[1:celular.index(')')].strip()
        numero = celular[celular.index(')') + 1:].strip()
        return ddd, numero
    return '', celular


class PesquisadorEditForm(forms.ModelForm):
    """Edição dos dados de um pesquisador já cadastrado."""
    nome = forms.CharField(max_length=150, label='Nome')
    ddd = forms.CharField(
        max_length=2,
        label='DDD',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ex.: 61',
            'inputmode': 'numeric',
            'maxlength': '2',
        }),
    )
    celular = forms.CharField(
        max_length=25,
        label='Celular',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ex.: 91234-5678'}),
    )
    email = forms.EmailField(label='E-mail')

    field_order = [
        'nome', 'formacao', 'ddd', 'celular',
        'preferencia_comunicacao_celular', 'email',
        'preferencia_comunicacao_email', 'whatsapp_apikey',
    ]

    class Meta:
        model = Pesquisador
        fields = [
            'formacao',
            'celular',
            'preferencia_comunicacao_celular',
            'preferencia_comunicacao_email',
            'whatsapp_apikey',
        ]
        labels = {
            'formacao': 'Formação',
            'preferencia_comunicacao_celular': 'Preferência de contato por celular',
            'preferencia_comunicacao_email': 'Preferência de contato por e-mail',
            'whatsapp_apikey': 'Chave WhatsApp (CallMeBot)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.instance.user
        self.fields['nome'].initial = user.get_full_name() or user.first_name
        self.fields['email'].initial = user.email
        ddd, numero = _separar_ddd_celular(self.instance.celular)
        self.fields['ddd'].initial = ddd
        self.fields['celular'].initial = numero

    def clean_ddd(self):
        ddd = (self.cleaned_data.get('ddd') or '').strip()
        if ddd and (not ddd.isdigit() or len(ddd) != 2):
            raise forms.ValidationError('Informe o DDD com 2 dígitos. Ex.: 61.')
        return ddd

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        existe = User.objects.filter(email__iexact=email).exclude(pk=self.instance.user_id)
        if existe.exists():
            raise forms.ValidationError('Já existe outro pesquisador cadastrado com este e-mail.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        ddd = (cleaned_data.get('ddd') or '').strip()
        celular = (cleaned_data.get('celular') or '').strip()
        if ddd and not celular:
            self.add_error('celular', 'Informe o número do celular junto com o DDD.')
        return cleaned_data

    def save(self, commit=True):
        pesquisador = super().save(commit=False)
        ddd = (self.cleaned_data.get('ddd') or '').strip()
        celular = (self.cleaned_data.get('celular') or '').strip()
        if ddd and celular:
            pesquisador.celular = f'({ddd}) {celular}'
        else:
            pesquisador.celular = celular or None

        user = pesquisador.user
        user.first_name = self.cleaned_data['nome']
        user.email = self.cleaned_data['email']
        user.save(update_fields=['first_name', 'email'])

        if commit:
            pesquisador.save()
        return pesquisador


def _admin_required(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
@user_passes_test(_admin_required)
def lista_pesquisadores(request):
    pesquisadores = (
        Pesquisador.objects.select_related('user').order_by('user__first_name', 'user__username')
    )
    return render(request, 'contas/lista_pesquisadores.html', {
        'pesquisadores': pesquisadores,
    })


@login_required
@user_passes_test(_admin_required)
def editar_pesquisador(request, pk):
    pesquisador = get_object_or_404(Pesquisador.objects.select_related('user'), pk=pk)

    if request.method == 'POST':
        form = PesquisadorEditForm(request.POST, instance=pesquisador)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pesquisador atualizado com sucesso.')
            return redirect('lista_pesquisadores')
    else:
        form = PesquisadorEditForm(instance=pesquisador)

    return render(request, 'contas/editar_pesquisador.html', {
        'form': form,
        'pesquisador': pesquisador,
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def registro_acoes(request):
    """Auditoria de ações — visível apenas para o super administrador."""
    registros = RegistroAcao.objects.select_related('user').all()

    usuario = request.GET.get('usuario', '').strip()
    if usuario:
        registros = registros.filter(username__icontains=usuario)

    registros = registros[:500]

    usuarios = (
        RegistroAcao.objects.values_list('username', flat=True).distinct().order_by('username')
    )

    return render(request, 'contas/registro_acoes.html', {
        'registros': registros,
        'usuarios': usuarios,
        'usuario_filtro': usuario,
    })