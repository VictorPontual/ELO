from collections import Counter
from datetime import date

from django.db.models import Count, Q
from django.db.models.functions import ExtractQuarter, ExtractYear
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


def _build_boolean_breakdown(queryset, field_name):
    return {
        'labels': ['Sim', 'Nao'],
        'values': [
            queryset.filter(**{field_name: True}).count(),
            queryset.filter(**{field_name: False}).count(),
        ],
    }

@login_required
def dashboard(request):
    hoje = date.today()
    trimestre_atual = ((hoje.month - 1) // 3) + 1

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

    estudos_andamento = Projeto.objects.filter(inicio_coleta__isnull=False).filter(
        Q(fim_coleta__isnull=True) | Q(fim_coleta__gte=hoje)
    ).count()

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

    tipo_data = list(
        aprovados_ano
        .exclude(tipo_pesq__isnull=True)
        .exclude(tipo_pesq__exact='')
        .values('tipo_pesq')
        .annotate(total=Count('sig_id_projeto'))
        .order_by('-total')[:8]
    )

    class_data = list(
        aprovados_ano
        .exclude(classificacoes__isnull=True)
        .values('classificacoes__nome_classificacao')
        .annotate(total=Count('sig_id_projeto', distinct=True))
        .order_by('-total')[:8]
    )

    linhas_counter = Counter()
    for projeto in aprovados_ano.only('linhas_pesq'):
        for linha in _parse_linhas_pesquisa(projeto.linhas_pesq):
            linhas_counter[linha] += 1

    top_linhas = linhas_counter.most_common(10)
    tabela_linhas = [{'linha': linha, 'total': total} for linha, total in top_linhas]

    charts = {
        'anual': {
            'labels': [str(item['ano']) for item in serie_anual],
            'values': [item['total'] for item in serie_anual],
        },
        'trimestral': {
            'labels': ['1o tri', '2o tri', '3o tri', '4o tri'],
            'values': [mapa_trimestres[1], mapa_trimestres[2], mapa_trimestres[3], mapa_trimestres[4]],
        },
        'tipo_pesquisa': {
            'labels': [item['tipo_pesq'] for item in tipo_data],
            'values': [item['total'] for item in tipo_data],
        },
        'classificacao': {
            'labels': [item['classificacoes__nome_classificacao'] for item in class_data],
            'values': [item['total'] for item in class_data],
        },
        'tecnologico': _build_boolean_breakdown(aprovados_ano, 'desenvolvimento_tecnologico'),
        'multicentrico': _build_boolean_breakdown(aprovados_ano, 'multicentrico'),
        'integracao': _build_boolean_breakdown(aprovados_ano, 'parceria_HUB_UNB'),
    }

    context = {
        'anos_disponiveis': anos_disponiveis,
        'ano_selecionado': ano_selecionado,
        'kpis': {
            'total_aprovados': total_aprovados_ano,
            'aprovados_trimestre': aprovados_trimestre,
            'estudos_andamento': estudos_andamento,
            'variacao_percentual': variacao_percentual,
            'ano_comparacao': ano_selecionado - 1,
        },
        'tabela_linhas': tabela_linhas,
        'charts': charts,
    }

    return render(request, 'dashboard/dashboard.html', context)
