"""Envio de avisos periódicos aos líderes dos projetos.

O canal é escolhido de acordo com a preferência de comunicação do pesquisador
(`preferencia_comunicacao_email` e/ou `preferencia_comunicacao_celular`):

- E-mail: usa o backend de e-mail configurado em settings.
- WhatsApp: usa a API gratuita do CallMeBot (https://www.callmebot.com/blog/free-api-whatsapp-messages/).
  Cada pesquisador precisa ter uma `whatsapp_apikey` gerada gratuitamente.

O envio é propositalmente isolado neste módulo: para trocar de provedor de
WhatsApp basta reescrever `enviar_whatsapp`.
"""

import logging
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import urlopen

from django.conf import settings
from django.core.mail import send_mail

from .models import AvisoEnviado, ConfiguracaoAviso, Participacao

logger = logging.getLogger(__name__)

CALLMEBOT_URL = 'https://api.callmebot.com/whatsapp.php'

FUNCAO_LIDER = 'Pesquisador principal'


def obter_lider(projeto):
    """Retorna o Pesquisador líder do projeto, ou o primeiro participante como fallback."""
    participacao = (
        Participacao.objects
        .filter(projeto=projeto, funcao__nome_funcao=FUNCAO_LIDER)
        .select_related('pesquisador__user')
        .first()
    )
    if participacao is None:
        participacao = (
            Participacao.objects
            .filter(projeto=projeto)
            .select_related('pesquisador__user')
            .first()
        )
    return participacao.pesquisador if participacao else None


def renderizar_mensagem(template, pesquisador, projeto):
    """Substitui as variáveis {nome}, {titulo} e {sig_id} no texto do aviso."""
    nome = pesquisador.user.get_full_name() or pesquisador.user.username
    contexto = {
        'nome': nome,
        'titulo': projeto.titulo,
        'sig_id': projeto.sig_id_projeto,
    }

    class _ComPadrao(dict):
        def __missing__(self, key):
            return '{' + key + '}'

    try:
        return template.format_map(_ComPadrao(contexto))
    except (ValueError, IndexError):
        # Texto com chaves malformadas: devolve o template original sem quebrar o envio.
        return template


def enviar_email(pesquisador, assunto, mensagem):
    """Envia o aviso por e-mail. Retorna (sucesso, detalhe)."""
    email = (pesquisador.user.email or '').strip()
    if not email:
        return False, 'Pesquisador sem e-mail cadastrado.'
    try:
        send_mail(
            assunto,
            mensagem,
            getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            [email],
            fail_silently=False,
        )
        return True, f'E-mail enviado para {email}.'
    except Exception as exc:  # noqa: BLE001 - registramos qualquer falha de envio
        logger.exception('Falha ao enviar e-mail de aviso')
        return False, f'Erro ao enviar e-mail: {exc}'


def enviar_whatsapp(pesquisador, mensagem):
    """Envia o aviso por WhatsApp via CallMeBot. Retorna (sucesso, detalhe)."""
    numero = (pesquisador.celular or '').strip()
    apikey = (pesquisador.whatsapp_apikey or '').strip()
    if not numero:
        return False, 'Pesquisador sem celular cadastrado.'
    if not apikey:
        return False, 'Pesquisador sem apikey do WhatsApp (CallMeBot) configurada.'

    numero_limpo = ''.join(ch for ch in numero if ch.isdigit() or ch == '+')
    url = (
        f'{CALLMEBOT_URL}?phone={quote(numero_limpo)}'
        f'&text={quote(mensagem)}&apikey={quote(apikey)}'
    )
    try:
        with urlopen(url, timeout=20) as resposta:
            corpo = resposta.read().decode('utf-8', errors='ignore')
        return True, f'WhatsApp enviado para {numero_limpo}. Resposta: {corpo[:200]}'
    except URLError as exc:
        logger.exception('Falha ao enviar WhatsApp de aviso')
        return False, f'Erro ao enviar WhatsApp: {exc}'


def _registrar(projeto, pesquisador, canal, destino, assunto, mensagem, sucesso, detalhe):
    return AvisoEnviado.objects.create(
        projeto=projeto,
        pesquisador=pesquisador,
        canal=canal,
        destino=destino,
        assunto=assunto,
        mensagem=mensagem,
        sucesso=sucesso,
        detalhe=detalhe,
    )


def renderizar_mensagem_alerta(template, pesquisador, projeto, config):
    """Renderiza a mensagem de um alerta (CEP/relatório) com suas variáveis."""
    nome = pesquisador.user.get_full_name() or pesquisador.user.username
    contexto = {
        'nome': nome,
        'titulo': projeto.titulo,
        'sig_id': projeto.sig_id_projeto,
        'data_aprovacao': projeto.data_aprovacao_inst.strftime('%d/%m/%Y') if projeto.data_aprovacao_inst else '-',
        'data_parecer_cep': projeto.data_parecer_cep.strftime('%d/%m/%Y') if projeto.data_parecer_cep else '-',
        'prazo_cep': config.prazo_cep_meses,
        'prazo_relatorio': config.prazo_relatorio_meses,
    }

    class _ComPadrao(dict):
        def __missing__(self, key):
            return '{' + key + '}'

    try:
        return template.format_map(_ComPadrao(contexto))
    except (ValueError, IndexError):
        return template


def enviar_cobranca_email(projeto, tipo, config=None):
    """Envia por e-mail a cobrança de um alerta (CEP ou relatório) ao pesquisador
    principal. Retorna (sucesso, detalhe)."""
    from .models import ConfiguracaoAlertas

    if config is None:
        config = ConfiguracaoAlertas.carregar()

    pesquisador = obter_lider(projeto)
    if pesquisador is None:
        return False, 'Projeto sem pesquisador principal associado.'

    if tipo == 'cep':
        assunto = config.assunto_cep
        template = config.mensagem_cep
    elif tipo == 'relatorio':
        assunto = config.assunto_relatorio
        template = config.mensagem_relatorio
    else:
        return False, 'Tipo de alerta inválido.'

    mensagem = renderizar_mensagem_alerta(template, pesquisador, projeto, config)
    sucesso, detalhe = enviar_email(pesquisador, assunto, mensagem)
    _registrar(
        projeto, pesquisador, 'email',
        (pesquisador.user.email or '').strip(),
        assunto, mensagem, sucesso, detalhe,
    )
    return sucesso, detalhe


def enviar_aviso_para_lider(projeto, config=None):
    """Envia o aviso ao líder do projeto pelos canais que ele prefere.

    Cria um registro `AvisoEnviado` para cada canal utilizado. Retorna a lista
    de registros criados (vazia quando não há líder ou preferência definida).
    """
    if config is None:
        config = ConfiguracaoAviso.carregar()

    pesquisador = obter_lider(projeto)
    if pesquisador is None:
        return []

    mensagem = renderizar_mensagem(config.mensagem, pesquisador, projeto)
    registros = []

    if pesquisador.preferencia_comunicacao_email:
        sucesso, detalhe = enviar_email(pesquisador, config.assunto, mensagem)
        registros.append(_registrar(
            projeto, pesquisador, 'email',
            (pesquisador.user.email or '').strip(),
            config.assunto, mensagem, sucesso, detalhe,
        ))

    if pesquisador.preferencia_comunicacao_celular:
        sucesso, detalhe = enviar_whatsapp(pesquisador, mensagem)
        registros.append(_registrar(
            projeto, pesquisador, 'whatsapp',
            (pesquisador.celular or '').strip(),
            config.assunto, mensagem, sucesso, detalhe,
        ))

    return registros
