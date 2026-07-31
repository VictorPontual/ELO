"""Context processors do app contas."""

from . import acesso


def navegacao_acesso(request):
    """Expõe, para os templates, o conjunto de áreas que o usuário pode ver.

    Usado no base.html para mostrar/esconder itens do menu conforme o acesso.
    """
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return {}
    return {'areas_visiveis': acesso.areas_visiveis(user)}
