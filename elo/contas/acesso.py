"""Controle de acesso por página (por usuário).

Cada "área" corresponde a uma página/seção do sistema. Um usuário pode ter, em
cada área, um destes níveis: sem acesso, ver, ou ver e editar. A ausência de
registro equivale a "sem acesso". O superusuário sempre tem acesso total.

O acesso é vinculado ao User do Django, que é criado a partir do login no AD.

Este módulo NÃO importa models no topo (só dentro das funções) para evitar
import circular, já que contas/models.py importa daqui.
"""

# --- Níveis de acesso (do menos para o mais permissivo) ---
NIVEL_NENHUM = 'nenhum'
NIVEL_VER = 'ver'
NIVEL_EDITAR = 'editar'

NIVEIS = [
    (NIVEL_NENHUM, 'Sem acesso'),
    (NIVEL_VER, 'Ver'),
    (NIVEL_EDITAR, 'Ver e editar'),
]

# --- Áreas controláveis (a ordem define a navegação e o destino de fallback) ---
AREA_PROJETOS = 'projetos'
AREA_DASHBOARD = 'dashboard'
AREA_PESQUISADORES = 'pesquisadores'
AREA_AVISOS = 'avisos'
AREA_AJUSTES = 'ajustes'
AREA_REGISTRO_ACOES = 'registro_acoes'

AREAS = [
    (AREA_PROJETOS, 'Projetos'),
    (AREA_DASHBOARD, 'Dashboard'),
    (AREA_PESQUISADORES, 'Pesquisadores'),
    (AREA_AVISOS, 'Avisos'),
    (AREA_AJUSTES, 'Ajustes'),
    (AREA_REGISTRO_ACOES, 'Registro de Ações'),
]

# Páginas de leitura: nelas o nível máximo é "ver" (não faz sentido "editar").
AREAS_SOMENTE_LEITURA = {AREA_DASHBOARD, AREA_REGISTRO_ACOES}

# url_name de destino de cada área (navegação e redirect de fallback).
AREA_URL = {
    AREA_PROJETOS: 'lista_projetos',
    AREA_DASHBOARD: 'dashboard',
    AREA_PESQUISADORES: 'lista_pesquisadores',
    AREA_AVISOS: 'gerenciar_avisos',
    AREA_AJUSTES: 'ajustes',
    AREA_REGISTRO_ACOES: 'registro_acoes',
}

# Mapa url_name -> área controlada. url_names ausentes NÃO são restringidos
# (login, logout, home, a própria gestão de acessos do superadmin, etc.).
# IMPORTANTE: ao criar uma nova página, adicione o url_name aqui.
URL_AREA = {
    # Projetos
    'lista_projetos': AREA_PROJETOS,
    'cadastro_projeto': AREA_PROJETOS,
    'editar_projeto': AREA_PROJETOS,
    'adicionar_pesquisador': AREA_PROJETOS,
    'remover_pesquisador': AREA_PROJETOS,
    'adicionar_unidade': AREA_PROJETOS,
    'remover_unidade': AREA_PROJETOS,
    'adicionar_hospital': AREA_PROJETOS,
    'remover_hospital': AREA_PROJETOS,
    'salvar_config_aviso': AREA_PROJETOS,
    'enviar_cobranca_alerta': AREA_PROJETOS,
    'criar_unidade_ajax': AREA_PROJETOS,
    'criar_hospital_ajax': AREA_PROJETOS,
    'criar_classificacao_ajax': AREA_PROJETOS,
    'criar_tipo_pesquisa_ajax': AREA_PROJETOS,
    'criar_sub_tipo_pesquisa_ajax': AREA_PROJETOS,
    'criar_linha_pesquisa_ajax': AREA_PROJETOS,
    'criar_especialidade_ajax': AREA_PROJETOS,
    'criar_instituicao_ajax': AREA_PROJETOS,
    'criar_vinculo_ajax': AREA_PROJETOS,
    'criar_funcao_ajax': AREA_PROJETOS,
    'criar_provedor_fomento_ajax': AREA_PROJETOS,
    # Avisos
    'gerenciar_avisos': AREA_AVISOS,
    'editar_aviso': AREA_AVISOS,
    'remover_aviso': AREA_AVISOS,
    # Ajustes
    'ajustes': AREA_AJUSTES,
    # Pesquisadores
    'lista_pesquisadores': AREA_PESQUISADORES,
    'cadastro': AREA_PESQUISADORES,
    'editar_pesquisador': AREA_PESQUISADORES,
    # Dashboard
    'dashboard': AREA_DASHBOARD,
    # Registro de ações (auditoria)
    'registro_acoes': AREA_REGISTRO_ACOES,
}

# Telas de edição/criação: exigem nível EDITAR para abrir (mesmo no GET), não
# apenas para salvar. As demais páginas exigem EDITAR só em métodos de escrita.
URLS_SEMPRE_EDITAR = {
    'cadastro_projeto', 'editar_projeto', 'enviar_cobranca_alerta',
    'cadastro', 'editar_pesquisador',
    'editar_aviso',
}

_SAFE_METHODS = {'GET', 'HEAD', 'OPTIONS'}


def nivel_do_usuario(user, area):
    """Retorna o nível ('nenhum'/'ver'/'editar') do usuário na área."""
    if not user or not user.is_authenticated:
        return NIVEL_NENHUM
    if user.is_superuser:
        return NIVEL_EDITAR
    from .models import AcessoPagina
    registro = AcessoPagina.objects.filter(user=user, area=area).first()
    return registro.nivel if registro else NIVEL_NENHUM


def pode_ver(user, area):
    return nivel_do_usuario(user, area) in (NIVEL_VER, NIVEL_EDITAR)


def pode_editar(user, area):
    return nivel_do_usuario(user, area) == NIVEL_EDITAR


def areas_visiveis(user):
    """Conjunto de áreas que o usuário pode ao menos ver (para a navegação)."""
    return {area for area, _ in AREAS if pode_ver(user, area)}


def primeira_area_acessivel(user):
    """url_name da primeira área que o usuário pode ver (destino de fallback)."""
    for area, _ in AREAS:
        if pode_ver(user, area):
            return AREA_URL[area]
    return None


def requer_editar(url_name, metodo):
    """Se a requisição exige nível EDITAR (escrita ou tela de edição)."""
    return metodo not in _SAFE_METHODS or url_name in URLS_SEMPRE_EDITAR
