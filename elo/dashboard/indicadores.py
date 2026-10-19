"""Cálculo dos indicadores dos dashboards.

Cada função recebe listas de objetos (projetos, eventos de etapa, itens de
orçamento, relatórios) e devolve dados prontos para o template e o Chart.js.
As views só montam o contexto.

Por enquanto os objetos vêm de `dados_mock.py`; os atributos usados aqui são
o contrato que a futura fonte (banco) precisa respeitar.

Séries para gráfico seguem o formato {'labels': [...], 'values': [...]}.
Tempos são em dias úteis (segunda a sexta; feriados não são descontados).
"""

import math
from collections import Counter, defaultdict
from decimal import Decimal
from statistics import median

# Etapas da tramitação: com quem fica, prazo e retorno previsto após devolução
# (dias úteis), conforme a proposta.
ETAPAS = [
    {'num': 1, 'nome': 'Cadastro e envio', 'com_quem': 'Pesquisador', 'prazo': 10, 'retorno': None},
    {'num': 2, 'nome': 'Análise documental', 'com_quem': 'UGPesq', 'prazo': 5, 'retorno': 5},
    {'num': 3, 'nome': 'Parecer das unidades', 'com_quem': 'Unidade', 'prazo': 10, 'retorno': 5},
    {'num': 4, 'nome': 'Parecer técnico e exequibilidade', 'com_quem': 'UGPesq', 'prazo': 3, 'retorno': 10},
    {'num': 5, 'nome': 'Carta de anuência', 'com_quem': 'Direção', 'prazo': 3, 'retorno': 5},
    {'num': 6, 'nome': 'Análise ética (CEP responsável)', 'com_quem': 'CEP externo', 'prazo': 30, 'retorno': 10},
    {'num': 7, 'nome': 'Validação e aprovação', 'com_quem': 'UGPesq', 'prazo': 2, 'retorno': 3},
    {'num': 8, 'nome': 'Início autorizado e acessos', 'com_quem': 'UGPesq', 'prazo': 5, 'retorno': 5},
]

# Etapas cujo tempo não é da instituição (ficam fora do "tempo líquido").
ETAPAS_EXTERNAS = {1, 6}
ETAPA_CEP = 6
ETAPA_APROVACAO = 7
ETAPA_INICIO = 8

# Tipos de evento de etapa.
ENTRADA = 'entrada'
DEVOLUCAO = 'devolucao'
REENVIO = 'reenvio'
CONCLUSAO = 'conclusao'
INATIVACAO = 'inativacao'

MOTIVOS_DEVOLUCAO = [
    'Documento ausente ou desatualizado',
    'Dado incoerente ou incompleto',
    'Exigência da unidade',
    'Condição da direção',
    'Pendência do CEP',
    'Termo ou acesso faltante',
    'Outro',
]

# Orçamento.
RUBRICAS = [
    'Pessoal e bolsas', 'Material de consumo', 'Equipamentos e material permanente',
    'Serviços de terceiros', 'Viagens e inscrições', 'Exames e procedimentos',
    'Medicamentos e insumos', 'Publicação e divulgação', 'Ressarcimento ao HU', 'Outro',
]
RUBRICA_RESSARCIMENTO = 'Ressarcimento ao HU'
FONTES = [
    'Fomento', 'Patrocinador', 'HU (contrapartida)',
    'Instituição de ensino ou pesquisa', 'Recurso próprio da equipe',
]
FONTE_HU = 'HU (contrapartida)'
FONTES_EXTERNAS = ('Fomento', 'Patrocinador')

# Relatórios de andamento.
REL_PENDENTE = 'pendente'
REL_ENTREGUE = 'entregue'
REL_ACEITO = 'aceito'
REL_DEVOLVIDO = 'devolvido'
META_ANALISE_RELATORIO = 5  # dias úteis
JANELA_VENCIMENTO_RELATORIO = 10  # dias úteis

NAO_INFORMADO = 'Não informado'


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def dias_uteis(inicio, fim):
    """Dias úteis de `inicio` (exclusive) até `fim` (inclusive). 0 se fim <= inicio."""
    if not inicio or not fim or fim <= inicio:
        return 0
    semanas, resto = divmod((fim - inicio).days, 7)
    total = semanas * 5
    dia_semana = inicio.weekday()
    for i in range(1, resto + 1):
        if (dia_semana + i) % 7 < 5:
            total += 1
    return total


def mediana(valores):
    valores = list(valores)
    return round(median(valores), 1) if valores else None


def percentil(valores, p):
    """Percentil pelo método do posto mais próximo (nearest-rank)."""
    valores = sorted(valores)
    if not valores:
        return None
    posto = max(1, math.ceil(p / 100 * len(valores)))
    return valores[posto - 1]


def percentual(parte, total):
    return round(100 * parte / total) if total else None


def serie(contagem, limite=None):
    """Counter -> {'labels', 'values'} em ordem decrescente."""
    itens = contagem.most_common(limite)
    return {
        'labels': [str(rotulo) for rotulo, _ in itens],
        'values': [float(v) if isinstance(v, Decimal) else v for _, v in itens],
    }


def parse_linhas_pesquisa(texto_linhas):
    if not texto_linhas:
        return []
    texto_normalizado = texto_linhas.replace(';', ',').replace('\n', ',')
    return [item.strip() for item in texto_normalizado.split(',') if item.strip()]


def contar(projetos, categorias_fn, limite=None):
    """Conta categorias (uma lista por projeto) e devolve a série."""
    contagem = Counter()
    for projeto in projetos:
        for categoria in categorias_fn(projeto):
            if categoria:
                contagem[categoria] += 1
    return serie(contagem, limite)


def par_sim_nao(projetos, valor_fn, rotulo_sim, rotulo_nao):
    """Par sim/não: contagens, rótulos e percentual do 'sim'."""
    sim = sum(1 for p in projetos if valor_fn(p))
    nao = len(projetos) - sim
    return {
        'rotulo_sim': rotulo_sim, 'sim': sim,
        'rotulo_nao': rotulo_nao, 'nao': nao,
        'pct_sim': percentual(sim, sim + nao),
    }


def dos_projetos(objetos, projetos):
    """Restringe eventos/itens/relatórios aos projetos informados (ex.: filtro por tipo)."""
    ids = {p.sig_id_projeto for p in projetos}
    return [o for o in objetos if o.projeto_id in ids]


def tipos_de_estudo(projetos):
    """Tipos de pesquisa presentes (para o filtro por tipo de estudo)."""
    return sorted({p.tipo_pesq for p in projetos if p.tipo_pesq})


# ---------------------------------------------------------------------------
# Painel
# ---------------------------------------------------------------------------

def aprovados(projetos):
    return [p for p in projetos if p.data_aprovacao_inst]


def em_andamento(projetos, hoje):
    """Coleta iniciada e sem encerramento (ou encerramento futuro)."""
    return [p for p in projetos if p.inicio_coleta and (not p.fim_coleta or p.fim_coleta >= hoje)]


def anos_aprovacao(projetos):
    return sorted({p.data_aprovacao_inst.year for p in aprovados(projetos)}, reverse=True)


def aprovacao_por_periodo(projetos, hoje):
    """Aprovações por trimestre e bimestre de cada ano, com o período em curso.

    {'anos': {ano: {'t': [4], 'b': [6]}}, 'atual': {'ano', 't', 'b'}} (índices 0-based).
    """
    anos = defaultdict(lambda: {'t': [0] * 4, 'b': [0] * 6})
    for p in aprovados(projetos):
        data = p.data_aprovacao_inst
        anos[data.year]['t'][(data.month - 1) // 3] += 1
        anos[data.year]['b'][(data.month - 1) // 2] += 1
    return {
        'anos': {str(ano): anos[ano] for ano in sorted(anos)},
        'atual': {
            'ano': str(hoje.year),
            't': (hoje.month - 1) // 3,
            'b': (hoje.month - 1) // 2,
        },
    }


def _eh_intervencao(projeto):
    """Metodologia derivada do tipo de pesquisa (não há campo próprio)."""
    tipo = (projeto.tipo_pesq or '').lower()
    return 'ensaio' in tipo or 'interven' in tipo


def situacao_estudos(projetos, eventos, hoje):
    """Concluídos, em andamento, aguardando início, em tramitação e inativados."""
    inativados = {e.projeto_id for e in eventos if e.tipo == INATIVACAO}
    contagem = Counter({
        'Concluídos': 0, 'Em andamento': 0, 'Aguardando início': 0, 'Em tramitação': 0,
    })
    for p in projetos:
        if p.fim_coleta and p.fim_coleta < hoje:
            contagem['Concluídos'] += 1
        elif p.inicio_coleta:
            contagem['Em andamento'] += 1
        elif p.data_aprovacao_inst:
            contagem['Aguardando início'] += 1
        elif p.sig_id_projeto in inativados:
            contagem['Inativados'] += 1
        else:
            contagem['Em tramitação'] += 1
    return serie(contagem)


def painel(projetos, eventos, ano, hoje):
    """Indicadores do Painel. `ano` recorta aprovações, barras e pares."""
    todos_aprovados = aprovados(projetos)
    aprovados_ano = [p for p in todos_aprovados if p.data_aprovacao_inst.year == ano]
    andamento = em_andamento(projetos, hoje)
    andamento_por_ano = Counter(p.inicio_coleta.year for p in andamento)
    anos_inicio = sorted(andamento_por_ano)

    return {
        'kpis': {
            'aprovados_acumulado': len(todos_aprovados),
            'primeiro_ano': min((p.data_aprovacao_inst.year for p in todos_aprovados), default=None),
            'em_andamento': len(andamento),
            'aprovados_ano': len(aprovados_ano),
            'multicentricos': sum(1 for p in aprovados_ano if p.multicentrico),
            'tecnologicos': sum(1 for p in aprovados_ano if p.desenvolvimento_tecnologico == 'sim'),
        },
        'periodo': aprovacao_por_periodo(projetos, hoje),
        'barras': {
            'andamento': {
                'labels': [str(a) for a in anos_inicio],
                'values': [andamento_por_ano[a] for a in anos_inicio],
            },
            'tipo': contar(aprovados_ano, lambda p: [p.tipo_pesq or NAO_INFORMADO], limite=10),
            'fomento': contar(aprovados_ano, lambda p: [p.tipo_fomento or NAO_INFORMADO], limite=10),
            'linhas': contar(aprovados_ano, lambda p: parse_linhas_pesquisa(p.linhas_pesq), limite=12),
            'classificacao': contar(aprovados_ano, lambda p: p.classificacoes),
            'situacao': situacao_estudos(projetos, eventos, hoje),
        },
        'pares': [
            {'titulo': 'Desenvolvimento tecnológico', **par_sim_nao(
                aprovados_ano, lambda p: p.desenvolvimento_tecnologico == 'sim',
                'Desenvolvimento tecnológico', 'Sem desenv. tecnológico')},
            {'titulo': 'Multicêntrico', **par_sim_nao(
                aprovados_ano, lambda p: p.multicentrico, 'Multicêntrico', 'Unicêntrico')},
            {'titulo': 'Com outro HU da rede Ebserh', **par_sim_nao(
                aprovados_ano, lambda p: p.com_outro_hu, 'Com outro HU', 'Somente o HU')},
            {'titulo': 'Integração HU–IES', **par_sim_nao(
                aprovados_ano, lambda p: p.parceria_HUB_UNB, 'Com integração', 'Sem integração')},
            {'titulo': 'Metodologia', **par_sim_nao(
                aprovados_ano, _eh_intervencao, 'Intervenção', 'Observacional')},
        ],
    }


# ---------------------------------------------------------------------------
# Eventos de etapa (base de Tempo e Mais indicadores)
# ---------------------------------------------------------------------------

def _analisar_eventos(eventos):
    """Percorre os eventos de UM projeto (em ordem) e resume cada etapa.

    Devolve (etapas, devolucoes, inativado):
    - etapas: {num: {'inicio', 'fim', 'liquido', 'devolucoes'}}; `liquido` são os
      dias úteis com o relógio correndo (exclui o tempo em devolução).
    - devolucoes: [{'etapa', 'data', 'previsao', 'reenvio', 'motivo'}].
    """
    etapas = {}
    devolucoes = []
    inativado = False
    for ev in eventos:
        if ev.tipo == INATIVACAO:
            inativado = True
            continue
        st = etapas.setdefault(ev.etapa, {
            'inicio': None, 'fim': None, 'liquido': 0, 'devolucoes': 0,
            '_rodando': None, '_dev': None,
        })
        if ev.tipo == ENTRADA:
            st['inicio'] = st['inicio'] or ev.data
            st['_rodando'] = ev.data
        elif ev.tipo == DEVOLUCAO:
            if st['_rodando']:
                st['liquido'] += dias_uteis(st['_rodando'], ev.data)
                st['_rodando'] = None
            st['devolucoes'] += 1
            st['_dev'] = {
                'etapa': ev.etapa, 'data': ev.data, 'previsao': ev.previsao_retorno,
                'reenvio': None, 'motivo': ev.motivo or NAO_INFORMADO,
            }
            devolucoes.append(st['_dev'])
        elif ev.tipo == REENVIO:
            if st['_dev'] and st['_dev']['reenvio'] is None:
                st['_dev']['reenvio'] = ev.data
            st['_rodando'] = ev.data
        elif ev.tipo == CONCLUSAO:
            if st['_rodando']:
                st['liquido'] += dias_uteis(st['_rodando'], ev.data)
                st['_rodando'] = None
            st['fim'] = ev.data
    for st in etapas.values():
        del st['_rodando'], st['_dev']
    return etapas, devolucoes, inativado


def analisar_tramitacao(eventos):
    """{projeto_id: {'etapas', 'devolucoes', 'inativado', 'ultimo_tipo'}}."""
    por_projeto = defaultdict(list)
    for ev in eventos:
        por_projeto[ev.projeto_id].append(ev)
    resultado = {}
    for pid, evs in por_projeto.items():
        evs.sort(key=lambda e: e.data)  # estável: mantém a ordem de registro no mesmo dia
        etapas, devolucoes, inativado = _analisar_eventos(evs)
        resultado[pid] = {
            'etapas': etapas, 'devolucoes': devolucoes, 'inativado': inativado,
            'ultimo_tipo': evs[-1].tipo,
        }
    return resultado


def _estatisticas_etapa(analise, etapa):
    """Mediana, P90, % no prazo e % devolvidos de uma etapa (etapas concluídas)."""
    info = ETAPAS[etapa - 1]
    entraram = [a['etapas'][etapa] for a in analise.values() if etapa in a['etapas']]
    tempos = [st['liquido'] for st in entraram if st['fim']]
    return {
        **info,
        'n': len(tempos),
        'mediana': mediana(tempos),
        'p90': percentil(tempos, 90),
        'pct_prazo': percentual(sum(1 for t in tempos if t <= info['prazo']), len(tempos)),
        'pct_devolvidos': percentual(sum(1 for st in entraram if st['devolucoes']), len(entraram)),
    }


def tempo_por_etapa(projetos, eventos):
    analise = analisar_tramitacao(dos_projetos(eventos, projetos))
    linhas = [_estatisticas_etapa(analise, e['num']) for e in ETAPAS]

    totais, liquidos = [], []
    for a in analise.values():
        fim = a['etapas'].get(ETAPA_INICIO, {}).get('fim')
        inicios = [st['inicio'] for st in a['etapas'].values() if st['inicio']]
        if not fim or not inicios:
            continue
        totais.append(dias_uteis(min(inicios), fim))
        liquidos.append(sum(
            st['liquido'] for num, st in a['etapas'].items() if num not in ETAPAS_EXTERNAS
        ))

    retornos = [
        dias_uteis(d['data'], d['reenvio'])
        for a in analise.values() for d in a['devolucoes'] if d['reenvio']
    ]
    internas = [l['pct_prazo'] for l in linhas if l['num'] not in ETAPAS_EXTERNAS and l['pct_prazo'] is not None]
    escala = max([l['p90'] or 0 for l in linhas] + [e['prazo'] for e in ETAPAS])

    return {
        'kpis': {
            'mediana_total': mediana(totais),
            'concluidos': len(totais),
            'mediana_liquido': mediana(liquidos),
            'mediana_cep': linhas[ETAPA_CEP - 1]['mediana'],
            'mediana_retorno': mediana(retornos),
            'pct_prazo_internas': round(sum(internas) / len(internas)) if internas else None,
        },
        'linhas': linhas,
        'escala': escala,
        'tem_eventos': bool(analise),
    }


# ---------------------------------------------------------------------------
# Mais indicadores
# ---------------------------------------------------------------------------

def relatorios_resumo(relatorios):
    entregues = [r for r in relatorios if r.entregue_em]
    return {
        'pct_no_prazo': percentual(sum(1 for r in entregues if r.entregue_em <= r.prazo), len(entregues)),
        'mediana_analise': mediana(
            dias_uteis(r.entregue_em, r.aceito_em) for r in relatorios if r.entregue_em and r.aceito_em
        ),
    }


def mais_indicadores(projetos, eventos, relatorios, hoje):
    analise = analisar_tramitacao(dos_projetos(eventos, projetos))
    relatorios = dos_projetos(relatorios, projetos)

    aprovados_fluxo = [a for a in analise.values() if a['etapas'].get(ETAPA_APROVACAO, {}).get('fim')]
    sem_devolucao = sum(
        1 for a in aprovados_fluxo
        if not any(d['etapa'] <= ETAPA_APROVACAO for d in a['devolucoes'])
    )
    devolucoes = [d for a in analise.values() for d in a['devolucoes']]
    com_previsao = [d for d in devolucoes if d['reenvio'] and d['previsao']]

    taxa_devolucao = {'labels': [], 'values': []}
    for etapa in ETAPAS[1:]:
        est = _estatisticas_etapa(analise, etapa['num'])
        if est['pct_devolvidos'] is not None:
            taxa_devolucao['labels'].append(f"{etapa['num']} {etapa['nome']}")
            taxa_devolucao['values'].append(est['pct_devolvidos'])

    cep = _estatisticas_etapa(analise, ETAPA_CEP)

    finais_aceitos = {r.projeto_id for r in relatorios if r.tipo == 'Final' and r.situacao == REL_ACEITO}
    com_relatorio_entregue = {r.projeto_id for r in relatorios if r.entregue_em}
    coleta_vencida = [p for p in projetos if p.fim_coleta and p.fim_coleta < hoje]

    return {
        'kpis': {
            'pct_primeira_passagem': percentual(sem_devolucao, len(aprovados_fluxo)),
            'aprovados_fluxo': len(aprovados_fluxo),
            'pct_reenvio_prazo': percentual(
                sum(1 for d in com_previsao if d['reenvio'] <= d['previsao']), len(com_previsao)
            ),
            'mediana_reenvio': mediana(dias_uteis(d['data'], d['reenvio']) for d in devolucoes if d['reenvio']),
            'inativados': sum(1 for a in analise.values() if a['inativado']),
            'devolvidos_agora': sum(1 for a in analise.values() if a['ultimo_tipo'] == DEVOLUCAO),
        },
        'taxa_devolucao': taxa_devolucao,
        'motivos': serie(Counter(d['motivo'] for d in devolucoes)),
        'etica': {
            'cep_mediana': cep['mediana'],
            'cep_p90': cep['p90'],
            'cep_pct_prazo': cep['pct_prazo'],
            'cep_prazo': cep['prazo'],
            'com_parecer': sum(1 for p in projetos if p.parecer_cep == 'sim'),
            'parecer_na': sum(1 for p in projetos if p.parecer_cep == 'na'),
        },
        'execucao': {
            **relatorios_resumo(relatorios),
            'coleta_vencida': len(coleta_vencida),
            'coleta_vencida_sem_relatorio': sum(
                1 for p in coleta_vencida if p.sig_id_projeto not in com_relatorio_entregue
            ),
            'pct_conclusao': percentual(
                sum(1 for p in coleta_vencida if p.sig_id_projeto in finais_aceitos), len(coleta_vencida)
            ),
        },
        'vinculos': contar(projetos, lambda p: p.vinculos),
        'especialidades': contar(projetos, lambda p: [p.especialidade_proponente], limite=10),
        'tem_eventos': bool(analise),
    }


# ---------------------------------------------------------------------------
# Financeiro
# ---------------------------------------------------------------------------

def _soma(itens):
    return sum((i.valor for i in itens), Decimal('0'))


def financeiro(projetos, itens_orcamento):
    projeto_por_id = {p.sig_id_projeto: p for p in projetos}
    itens = dos_projetos(itens_orcamento, projetos)
    por_projeto = defaultdict(list)
    for item in itens:
        por_projeto[item.projeto_id].append(item)

    custo_hu = _soma(i for i in itens if i.fonte == FONTE_HU)
    ressarcimento = _soma(i for i in itens if i.rubrica == RUBRICA_RESSARCIMENTO)

    por_fonte, por_rubrica, por_tipo = Counter(), Counter(), Counter()
    for item in itens:
        por_fonte[item.fonte] += item.valor
        por_rubrica[item.rubrica] += item.valor
        por_tipo[projeto_por_id[item.projeto_id].tipo_pesq or NAO_INFORMADO] += item.valor

    maiores = []
    for pid, lista in por_projeto.items():
        projeto = projeto_por_id[pid]
        maiores.append({
            'codigo': pid,
            'titulo': projeto.titulo,
            'tipo': projeto.tipo_pesq or NAO_INFORMADO,
            'total': _soma(lista),
            'custo_hu': _soma(i for i in lista if i.fonte == FONTE_HU),
            'ressarcimento': _soma(i for i in lista if i.rubrica == RUBRICA_RESSARCIMENTO),
        })
    maiores.sort(key=lambda m: m['total'], reverse=True)

    return {
        'kpis': {
            'total': _soma(itens),
            'externos': _soma(i for i in itens if i.fonte in FONTES_EXTERNAS),
            'custo_hu': custo_hu,
            'ressarcimento': ressarcimento,
            'saldo_hu': ressarcimento - custo_hu,
            'mediana_estudo': median([m['total'] for m in maiores]) if maiores else None,
            'com_orcamento': len(por_projeto),
            'total_estudos': len(projetos),
        },
        'barras': {
            'fonte': serie(por_fonte),
            'rubrica': serie(por_rubrica),
            'tipo': serie(por_tipo),
        },
        'maiores': maiores[:8],
    }


# ---------------------------------------------------------------------------
# Relatórios de andamento
# ---------------------------------------------------------------------------

def _aberto(rel):
    return rel.situacao in (REL_PENDENTE, REL_DEVOLVIDO)


def _atrasado(rel, hoje):
    return _aberto(rel) and rel.prazo < hoje


FILTROS_RELATORIO = {
    'todos': ('Todos', lambda r, hoje: True),
    'a_entregar': ('A entregar', lambda r, hoje: r.situacao == REL_PENDENTE and not _atrasado(r, hoje)),
    'atraso': ('Em atraso', _atrasado),
    'analise': ('Aguardando análise', lambda r, hoje: r.situacao == REL_ENTREGUE),
    'aceitos': ('Aceitos', lambda r, hoje: r.situacao == REL_ACEITO),
    'devolvidos': ('Devolvidos', lambda r, hoje: r.situacao == REL_DEVOLVIDO),
}


def _situacao_relatorio(rel, hoje):
    """(rótulo, classe css) da situação exibida na lista."""
    if rel.situacao == REL_ACEITO:
        texto = f'Aceito em {rel.aceito_em:%d/%m/%Y}' if rel.aceito_em else 'Aceito'
        return texto, 'ok'
    if rel.situacao == REL_ENTREGUE:
        return 'Aguardando análise', 'aviso'
    if _atrasado(rel, hoje):
        return 'Em atraso', 'ruim'
    if rel.situacao == REL_DEVOLVIDO:
        return 'Devolvido', 'ruim'
    return 'A entregar', 'aviso'


def relatorios(projetos, relatorios_andamento, hoje, filtro='todos'):
    if filtro not in FILTROS_RELATORIO:
        filtro = 'todos'
    projeto_por_id = {p.sig_id_projeto: p for p in projetos}
    rels = dos_projetos(relatorios_andamento, projetos)
    abertos = [r for r in rels if _aberto(r)]
    atrasados = [r for r in abertos if _atrasado(r, hoje)]

    _, condicao = FILTROS_RELATORIO[filtro]
    selecionados = sorted(
        (r for r in rels if condicao(r, hoje)),
        key=lambda r: (not _atrasado(r, hoje), r.prazo),
    )
    linhas = []
    for rel in selecionados:
        projeto = projeto_por_id[rel.projeto_id]
        texto, classe = _situacao_relatorio(rel, hoje)
        linhas.append({
            'codigo': rel.projeto_id,
            'titulo': projeto.titulo,
            'coordenacao': projeto.coordenacao or '—',
            'tipo': rel.tipo,
            'periodo': rel.periodo or 'a informar',
            'prazo': rel.prazo,
            'situacao': texto,
            'classe': classe,
        })

    return {
        'kpis': {
            'a_entregar': len(abertos),
            'em_atraso': len(atrasados),
            'vencem_em_breve': sum(
                1 for r in abertos
                if not _atrasado(r, hoje) and dias_uteis(hoje, r.prazo) <= JANELA_VENCIMENTO_RELATORIO
            ),
            'aguardando_analise': sum(1 for r in rels if r.situacao == REL_ENTREGUE),
            **relatorios_resumo(rels),
            'meta_analise': META_ANALISE_RELATORIO,
            'janela_vencimento': JANELA_VENCIMENTO_RELATORIO,
        },
        'filtros': [(chave, rotulo) for chave, (rotulo, _) in FILTROS_RELATORIO.items()],
        'filtro': filtro,
        'linhas': linhas,
    }
