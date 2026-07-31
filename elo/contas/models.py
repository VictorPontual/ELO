from django.db import models
from django.contrib.auth.models import User

from .acesso import AREAS, NIVEIS, NIVEL_NENHUM

# Create your models here.


class AcessoPagina(models.Model):
    """Nível de acesso de um usuário a uma página/área do sistema.

    A ausência de registro equivale a "sem acesso". O superusuário sempre tem
    acesso total (tratado no código, sem depender destes registros)."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='acessos_pagina'
    )
    area = models.CharField(max_length=30, choices=AREAS)
    nivel = models.CharField(max_length=10, choices=NIVEIS, default=NIVEL_NENHUM)

    class Meta:
        unique_together = ('user', 'area')
        verbose_name = 'Acesso a Página'
        verbose_name_plural = 'Acessos a Páginas'

    def __str__(self):
        return f'{self.user.username} · {self.area} · {self.nivel}'


class SessaoAtiva(models.Model):
    """Registra a sessão ativa de cada usuário para impedir uso simultâneo em
    dispositivos diferentes. Ao logar em um novo dispositivo, a sessão anterior
    é invalidada."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sessao_ativa')
    session_key = models.CharField(max_length=40, db_index=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sessão Ativa'
        verbose_name_plural = 'Sessões Ativas'

    def __str__(self):
        return f'Sessão de {self.user.username}'


class RegistroAcao(models.Model):
    """Registro de ações realizadas pelas contas, visível apenas ao super admin."""

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acoes'
    )
    username = models.CharField(max_length=150, blank=True)
    acao = models.CharField(max_length=255)
    metodo = models.CharField(max_length=10, blank=True)
    caminho = models.CharField(max_length=255, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Registro de Ação'
        verbose_name_plural = 'Registros de Ações'

    def __str__(self):
        return f'{self.username or "?"} - {self.acao} ({self.criado_em:%d/%m/%Y %H:%M})'

class Pesquisador(models.Model):
    FORMACAO_CHOICES = [
        ('graduacao', 'Graduação'),
        ('mestrado', 'Mestrado'),
        ('doutorado', 'Doutorado'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    formacao = models.CharField(max_length=15, choices=FORMACAO_CHOICES, default='graduacao')
    celular = models.CharField(max_length=25, blank=True, null=True)
    preferencia_comunicacao_celular = models.BooleanField(default=False)
    preferencia_comunicacao_email = models.BooleanField(default=False)
    whatsapp_apikey = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=(
            'Chave (apikey) gratuita do CallMeBot para envio de WhatsApp. '
            'O pesquisador gera a chave adicionando o contato do CallMeBot e '
            'enviando a mensagem de autorização. Necessária apenas se a '
            'preferência de comunicação for por celular/WhatsApp.'
        ),
    )
    
    class Meta:
        db_table = 'pesquisador'
    
    def __str__(self):
        return self.user.get_full_name()
