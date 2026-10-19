from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from . import dados_mock, indicadores


def _safe_int(value, fallback):
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _filtro_tipo(request, projetos):
    """Aplica o filtro ?tipo= (tipo de estudo) e devolve o contexto do seletor."""
    tipos = indicadores.tipos_de_estudo(projetos)
    tipo = request.GET.get('tipo', '')
    if tipo not in tipos:
        tipo = ''
    if tipo:
        projetos = [p for p in projetos if p.tipo_pesq == tipo]
    return projetos, {'tipos': tipos, 'tipo_selecionado': tipo}


@login_required
def dashboard(request):
    """Painel: aprovações, andamento e perfil dos estudos aprovados no ano."""
    hoje = date.today()
    dados = dados_mock.carregar(hoje)

    anos_disponiveis = indicadores.anos_aprovacao(dados.projetos)
    ano_padrao = anos_disponiveis[0] if anos_disponiveis else hoje.year
    ano_selecionado = _safe_int(request.GET.get('ano'), ano_padrao)
    if anos_disponiveis and ano_selecionado not in anos_disponiveis:
        ano_selecionado = ano_padrao

    painel = indicadores.painel(dados.projetos, dados.eventos, ano_selecionado, hoje)
    context = {
        'aba': 'painel',
        'anos_disponiveis': anos_disponiveis,
        'ano_selecionado': ano_selecionado,
        'ano_atual': hoje.year,
        'kpis': painel['kpis'],
        'pares': painel['pares'],
        'charts': {'periodo': painel['periodo'], **painel['barras']},
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def mais_indicadores(request):
    hoje = date.today()
    dados = dados_mock.carregar(hoje)
    mais = indicadores.mais_indicadores(dados.projetos, dados.eventos, dados.relatorios, hoje)
    context = {
        'aba': 'mais',
        **mais,
        'charts': {
            'taxa_devolucao': mais['taxa_devolucao'],
            'motivos': mais['motivos'],
            'vinculos': mais['vinculos'],
            'especialidades': mais['especialidades'],
        },
    }
    return render(request, 'dashboard/mais.html', context)


@login_required
def tempo_por_etapa(request):
    dados = dados_mock.carregar()
    projetos, filtro = _filtro_tipo(request, dados.projetos)
    context = {
        'aba': 'tempo',
        **filtro,
        **indicadores.tempo_por_etapa(projetos, dados.eventos),
    }
    return render(request, 'dashboard/tempo.html', context)


@login_required
def financeiro(request):
    dados = dados_mock.carregar()
    projetos, filtro = _filtro_tipo(request, dados.projetos)
    fin = indicadores.financeiro(projetos, dados.itens_orcamento)
    context = {
        'aba': 'financeiro',
        **filtro,
        **fin,
        'charts': fin['barras'],
    }
    return render(request, 'dashboard/financeiro.html', context)


@login_required
def relatorios(request):
    hoje = date.today()
    dados = dados_mock.carregar(hoje)
    context = {
        'aba': 'relatorios',
        **indicadores.relatorios(dados.projetos, dados.relatorios, hoje, request.GET.get('situacao', 'todos')),
    }
    return render(request, 'dashboard/relatorios.html', context)
