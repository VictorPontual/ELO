from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse


class SessaoUnicaMiddleware:
    """Garante que cada conta tenha apenas uma sessão ativa por vez.

    Se a conta for usada em outro dispositivo, a sessão atual (mais antiga) é
    encerrada assim que fizer a próxima requisição.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            from .models import SessaoAtiva

            session_key = request.session.session_key
            registro = SessaoAtiva.objects.filter(user=user).first()

            if registro is None:
                # Adota a sessão atual (usuários já logados antes do recurso).
                if session_key:
                    SessaoAtiva.objects.create(user=user, session_key=session_key)
            elif session_key and registro.session_key != session_key:
                # A conta foi usada em outro dispositivo: encerra esta sessão.
                logout(request)
                messages.error(
                    request,
                    'Sua sessão foi encerrada porque esta conta foi acessada em outro dispositivo.',
                )
                if request.path != reverse('login'):
                    return redirect('login')

        return self.get_response(request)


# Nomes de ação legíveis por rota (url_name). Fallback: o próprio url_name.
ACOES_LEGIVEIS = {
    'cadastro_projeto': 'Cadastrou um projeto',
    'editar_projeto': 'Editou um projeto',
    'adicionar_pesquisador': 'Adicionou pesquisador a um projeto',
    'remover_pesquisador': 'Removeu pesquisador de um projeto',
    'adicionar_unidade': 'Adicionou unidade a um projeto',
    'remover_unidade': 'Removeu unidade de um projeto',
    'adicionar_hospital': 'Adicionou hospital a um projeto',
    'remover_hospital': 'Removeu hospital de um projeto',
    'salvar_config_aviso': 'Atualizou configuração de avisos',
    'cadastro': 'Cadastrou um pesquisador',
    'editar_pesquisador': 'Editou um pesquisador',
    'login': 'Efetuou login',
    'logout': 'Efetuou logout',
}


def _obter_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class RegistroAcoesMiddleware:
    """Registra ações de escrita (POST) das contas para auditoria do super admin."""

    METODOS_REGISTRAVEIS = {'POST', 'PUT', 'PATCH', 'DELETE'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            user = getattr(request, 'user', None)
            if (
                user and user.is_authenticated
                and request.method in self.METODOS_REGISTRAVEIS
                and response.status_code < 500
            ):
                url_name = getattr(getattr(request, 'resolver_match', None), 'url_name', None)
                acao = ACOES_LEGIVEIS.get(url_name, url_name or request.path)
                from .models import RegistroAcao
                RegistroAcao.objects.create(
                    user=user,
                    username=user.get_username(),
                    acao=acao,
                    metodo=request.method,
                    caminho=request.path[:255],
                    ip=_obter_ip(request),
                )
        except Exception:  # noqa: BLE001 - auditoria nunca deve quebrar a requisição
            pass

        return response


class AdminOnlyAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated and not (user.is_staff or user.is_superuser):
            if request.path != reverse('logout'):
                logout(request)
                messages.error(request, 'Acesso permitido apenas para contas administrativas.')
                return redirect('login')

        return self.get_response(request)
