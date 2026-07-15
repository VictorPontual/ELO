"""Sinais que garantem apenas uma sessão ativa por usuário."""

from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.dispatch import receiver
from django.utils import timezone

from .models import SessaoAtiva


@receiver(user_logged_in)
def registrar_sessao_unica(sender, request, user, **kwargs):
    """Ao autenticar, invalida a sessão anterior e registra a atual."""
    if not request.session.session_key:
        request.session.save()
    nova_key = request.session.session_key

    registro = SessaoAtiva.objects.filter(user=user).first()
    if registro and registro.session_key and registro.session_key != nova_key:
        # Remove a sessão do dispositivo anterior (logout forçado nele).
        Session.objects.filter(session_key=registro.session_key).delete()

    SessaoAtiva.objects.update_or_create(
        user=user,
        defaults={'session_key': nova_key, 'atualizado_em': timezone.now()},
    )
