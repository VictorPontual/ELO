from collections import Counter, defaultdict
from datetime import date

from django.db.models import Count, Q
from django.db.models.functions import ExtractMonth, ExtractQuarter, ExtractYear
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from projetos.models import Projeto


def _parse_linhas_pesquisa(texto_linhas):
    if not texto_linhas:
        return []

    texto_normalizado = texto_linhas.replace(';', ',').replace('\n', ',')
    return [item.strip() for item in texto_normalizado.split(',') if item.strip()]


def _safe_int(value, fallback):
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _trimestre_idx(d):
    """Índice 0..3 do trimestre de uma data."""
    return (d.month - 1) // 3


def _breakdown(projetos, categorias_fn, limite=None):
    """Conta categorias no total e por trimestre (no ano já filtrado).

    `categorias_fn(projeto)` devolve uma lista de categorias (permite M2M e
    linhas de pesquisa múltiplas). Retorna
    {labels, total, trimestres:[[q1..],[q2..],[q3..],[q4..]]} alinhado a labels.
    """
    total = Counter()
    por_q = defaultdict(lambda: [0, 0, 0, 0])
    for projeto in projetos:
        if not projeto.data_aprovacao_inst:
            continue
        q = _trimestre_idx(projeto.data_aprovacao_inst)
        for cat in categorias_fn(projeto):
            if not cat:
                continue
            total[cat] += 1
            por_q[cat][q] += 1
    itens = total.most_common(limite)
    labels = [c for c, _ in itens]
    return {
        'labels': labels,
        'total': [n for _, n in itens],
        'trimestres': [[por_q[c][qi] for c in labels] for qi in range(4)],
    }


def _breakdown_bool(projetos, valor_fn):
    """Breakdown Sim/Não (ordem fixa) no total e por trimestre."""
    total = [0, 0]
    trimestres = [[0, 0] for _ in range(4)]
    for projeto in projetos:
        if not projeto.data_aprovacao_inst:
            continue
        idx = 0 if valor_fn(projeto) else 1
        total[idx] += 1
        trimestres[_trimestre_idx(projeto.data_aprovacao_inst)][idx] += 1
    return {'labels': ['Sim', 'Não'], 'total': total, 'trimestres': trimestres}


@login_required
def dashboard(request):
    hoje = date.today()
    trimestre_atual = ((hoje.month - 1) // 3) + 1
    bimestre_atual = ((hoje.month - 1) // 2) + 1

    projetos_aprovados = Projeto.objects.exclude(data_aprovacao_inst__isnull=True)

    anos_disponiveis = list(
        projetos_aprovados
        .annotate(ano=ExtractYear('data_aprovacao_inst'))
        .values_list('ano', flat=True)
        .distinct()
        .order_by('-ano')
    )

    ano_padrao = anos_disponiveis[0] if anos_disponiveis else hoje.year
    ano_selecionado = _safe_int(request.GET.get('ano'), ano_padrao)
    if anos_disponiveis and ano_selecionado not in anos_disponiveis:
        ano_selecionado = ano_padrao

    aprovados_ano = projetos_aprovados.filter(data_aprovacao_inst__year=ano_selecionado)
    total_aprovados_ano = aprovados_ano.count()
    total_aprovados_ano_anterior = projetos_aprovados.filter(
        data_aprovacao_inst__year=ano_selecionado - 1
    ).count()

    if total_aprovados_ano_anterior > 0:
        variacao_percentual = round(
            ((total_aprovados_ano - total_aprovados_ano_anterior) / total_aprovados_ano_anterior) * 100,
            1,
        )
    else:
        variacao_percentual = None

    aprovados_trimestre = aprovados_ano.filter(
        data_aprovacao_inst__quarter=trimestre_atual
    ).count()

    meses_bimestre_atual = [2 * bimestre_atual - 1, 2 * bimestre_atual]
    aprovados_bimestre = aprovados_ano.filter(
        data_aprovacao_inst__month__in=meses_bimestre_atual
    ).count()

    estudos_andamento_qs = Projeto.objects.filter(inicio_coleta__isnull=False).filter(
        Q(fim_coleta__isnull=True) | Q(fim_coleta__gte=hoje)
    )
    estudos_andamento = estudos_andamento_qs.count()

    # --- Painel Tempo ---
    serie_anual = list(
        projetos_aprovados
        .annotate(ano=ExtractYear('data_aprovacao_inst'))
        .values('ano')
        .annotate(total=Count('sig_id_projeto'))
        .order_by('ano')
    )

    mapa_trimestres = {1: 0, 2: 0, 3: 0, 4: 0}
    trimestral = (
        aprovados_ano
        .annotate(trimestre=ExtractQuarter('data_aprovacao_inst'))
        .values('trimestre')
        .annotate(total=Count('sig_id_projeto'))
    )
    for item in trimestral:
        mapa_trimestres[item['trimestre']] = item['total']

    mapa_bimestres = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    por_mes = (
        aprovados_ano
        .annotate(mes=ExtractMonth('data_aprovacao_inst'))
        .values('mes')
        .annotate(total=Count('sig_id_projeto'))
    )
    for item in por_mes:
        bimestre = ((item['mes'] - 1) // 2) + 1
        mapa_bimestres[bimestre] += item['total']

    # Estudos em andamento por ano de início da coleta.
    serie_andamento = Counter(
        p.inicio_coleta.year for p in estudos_andamento_qs.only('inicio_coleta')
    )
    anos_andamento = sorted(serie_andamento)

    # --- Painel Distribuição (dimensões com total + por trimestre) ---
    projetos_ano = list(aprovados_ano.prefetch_related('classificacoes', 'hospitais_parceiros'))

    dist = {
        'tipo_pesquisa': {
            **_breakdown(projetos_ano, lambda p: [p.tipo_pesq], limite=10),
            'tipo': 'barra',
        },
        'fomento': {
            **_breakdown(projetos_ano, lambda p: [p.tipo_fomento], limite=10),
            'tipo': 'barra',
        },
        'classificacao': {
            **_breakdown(
                projetos_ano,
                lambda p: [c.nome_classificacao for c in p.classificacoes.all()],
                limite=10,
            ),
            'tipo': 'barra',
        },
        'linhas': {
            **_breakdown(projetos_ano, lambda p: _parse_linhas_pesquisa(p.linhas_pesq), limite=12),
            'tipo': 'barra',
        },
        'tecnologico': {
            **_breakdown(
                projetos_ano,
                lambda p: [p.get_desenvolvimento_tecnologico_display() or '(não informado)'],
            ),
            'tipo': 'rosca',
        },
        'multicentrico': {
            **_breakdown_bool(projetos_ano, lambda p: p.multicentrico),
            'tipo': 'rosca',
        },
        'integracao': {
            **_breakdown_bool(projetos_ano, lambda p: p.parceria_HUB_UNB),
            'tipo': 'rosca',
        },
        # "Realizado em conjunto com outros HUs da Rede HUBrasil": derivado da
        # existência de hospitais parceiros vinculados ao projeto.
        'rede_hubrasil': {
            **_breakdown_bool(projetos_ano, lambda p: len(p.hospitais_parceiros.all()) > 0),
            'tipo': 'rosca',
        },
    }

    # Linhas de pesquisa: submetidos (entrada no SIG no ano) x aprovados no ano.
    submetidos_linha = Counter()
    for p in Projeto.objects.filter(data_ent_sig__year=ano_selecionado).only('linhas_pesq'):
        for linha in _parse_linhas_pesquisa(p.linhas_pesq):
            submetidos_linha[linha] += 1
    aprovados_linha = Counter()
    for p in projetos_ano:
        for linha in _parse_linhas_pesquisa(p.linhas_pesq):
            aprovados_linha[linha] += 1
    labels_sa = [linha for linha, _ in (submetidos_linha + aprovados_linha).most_common(12)]
    dist['linhas_sub_aprov'] = {
        'labels': labels_sa,
        'submetidos': [submetidos_linha[linha] for linha in labels_sa],
        'aprovados': [aprovados_linha[linha] for linha in labels_sa],
        'tipo': 'sub_aprov',
    }

    charts = {
        'anual': {
            'labels': [str(item['ano']) for item in serie_anual],
            'values': [item['total'] for item in serie_anual],
        },
        'trimestral': {
            'labels': ['1o tri', '2o tri', '3o tri', '4o tri'],
            'values': [mapa_trimestres[1], mapa_trimestres[2], mapa_trimestres[3], mapa_trimestres[4]],
        },
        'bimestral': {
            'labels': ['1o bim', '2o bim', '3o bim', '4o bim', '5o bim', '6o bim'],
            'values': [mapa_bimestres[i] for i in range(1, 7)],
        },
        'andamento': {
            'labels': [str(ano) for ano in anos_andamento],
            'values': [serie_andamento[ano] for ano in anos_andamento],
        },
        'dist': dist,
    }

    context = {
        'anos_disponiveis': anos_disponiveis,
        'ano_selecionado': ano_selecionado,
        'kpis': {
            'total_aprovados': total_aprovados_ano,
            'aprovados_trimestre': aprovados_trimestre,
            'aprovados_bimestre': aprovados_bimestre,
            'bimestre_atual': bimestre_atual,
            'estudos_andamento': estudos_andamento,
            'variacao_percentual': variacao_percentual,
            'ano_comparacao': ano_selecionado - 1,
        },
        'charts': charts,
    }

    return render(request, 'dashboard/dashboard.html', context)
