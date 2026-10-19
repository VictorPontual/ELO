"""Dados de exemplo (mock) dos dashboards.

Os dashboards ainda não estão ligados ao banco: projetos, eventos de
tramitação, orçamento e relatórios são gerados aqui, sempre iguais (semente
fixa) e com datas relativas ao dia de hoje.

Para ligar ao banco, troque `carregar()` por consultas que devolvam objetos
com os mesmos atributos das dataclasses abaixo (é o que `indicadores.py` usa).
"""

import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from functools import lru_cache

from . import indicadores as ind

SEMENTE = 2026
QUANTIDADE_PROJETOS = 160


@dataclass
class ProjetoMock:
    sig_id_projeto: str
    titulo: str
    tipo_pesq: str
    tipo_fomento: str | None
    multicentrico: bool
    desenvolvimento_tecnologico: str
    parceria_HUB_UNB: bool
    com_outro_hu: bool
    linhas_pesq: str
    especialidade_proponente: str
    classificacoes: list = field(default_factory=list)
    data_aprovacao_inst: date | None = None
    inicio_coleta: date | None = None
    fim_coleta: date | None = None
    parecer_cep: str | None = None
    coordenacao: str = ''
    vinculos: list = field(default_factory=list)


@dataclass
class EventoEtapaMock:
    projeto_id: str
    etapa: int
    tipo: str
    data: date
    motivo: str = ''
    previsao_retorno: date | None = None


@dataclass
class ItemOrcamentoMock:
    projeto_id: str
    rubrica: str
    fonte: str
    valor: Decimal


@dataclass
class RelatorioMock:
    projeto_id: str
    tipo: str
    periodo: str
    prazo: date
    situacao: str
    entregue_em: date | None = None
    aceito_em: date | None = None


@dataclass
class DadosDashboard:
    projetos: list
    eventos: list
    itens_orcamento: list
    relatorios: list


# --- Vocabulário dos dados de exemplo (pesos aproximados) ---
TIPOS = {
    'Observacional': 34, 'Ensaio clínico': 14, 'Qualitativo': 13,
    'Dados secundários': 11, 'Desenvolvimento tecnológico': 9, 'Ensino, serviço e gestão': 7,
}
FOMENTOS = {
    'PRÓPRIO PESQUISADOR': 40, 'EDITAL DE AGÊNCIAS DE FOMENTO': 18, 'PÚBLICO NACIONAL': 12,
    'PRIVADO NACIONAL': 7, 'PRIVADO INTERNACIONAL': 5, 'OUTRA': 3, None: 15,
}
CLASSIFICACOES = {'Acadêmica': 84, 'Institucional': 11, 'Patrocinada': 5}
LINHAS = [
    'Oncologia', 'Saúde da mulher', 'Cardiologia', 'Infectologia', 'Saúde mental',
    'Pediatria e neonatologia', 'Endocrinologia', 'Nefrologia', 'Cirurgia', 'Gestão e serviços',
]
VINCULOS = {
    'Servidor Ebserh no HU': 18, 'Docente de IES com atuação no HU': 15,
    'Docente de IES (sem atuação no HU)': 11, 'Pós-graduando': 20, 'Graduando': 24,
    'Residente do HU': 8, 'Pesquisador de outra instituição': 6,
}
COORDENACAO = [
    'Ana Exemplo Alfa', 'Bruno Exemplo Beta', 'Clara Exemplo Gama', 'Daniel Exemplo Delta',
    'Elisa Exemplo Épsilon', 'Fábio Exemplo Zeta', 'Gabriela Exemplo Eta', 'Heitor Exemplo Teta',
]
TEMAS = [
    'resposta a imunoterapia em carcinoma de pulmão', 'vitamina D no pós-operatório',
    'vivências da enfermagem na UTI neonatal', 'sensor vestível para arritmias',
    'sepse e resistência antimicrobiana', 'tempo de espera no pronto-socorro',
    'adesão ao tratamento na doença renal crônica', 'reabilitação pós-AVC com realidade virtual',
    'saúde mental de residentes', 'satisfação com a escala de enfermagem',
    'desfechos de diabetes gestacional', 'dor crônica na atenção ambulatorial',
    'telemonitoramento de insuficiência cardíaca', 'aleitamento materno na alta hospitalar',
    'infecção de sítio cirúrgico', 'qualidade de vida após transplante renal',
]
# Probabilidade de devolução em cada etapa (1 a 8) e motivo mais provável.
CHANCE_DEVOLUCAO = [0, .30, .12, .22, .08, .26, .05, .10]
MOTIVO_POR_ETAPA = {
    2: 'Documento ausente ou desatualizado', 3: 'Exigência da unidade', 4: 'Dado incoerente ou incompleto',
    5: 'Condição da direção', 6: 'Pendência do CEP', 7: 'Documento ausente ou desatualizado',
    8: 'Termo ou acesso faltante',
}
CHANCE_INATIVACAO = 0.12  # entre as devoluções


def _escolher(rng, pesos):
    return rng.choices(list(pesos), weights=list(pesos.values()))[0]


def _somar_uteis(data, dias):
    """Data `dias` úteis depois de `data`."""
    while dias > 0:
        data += timedelta(days=1)
        if data.weekday() < 5:
            dias -= 1
    return data


def _somar_meses(data, meses):
    total = data.month - 1 + meses
    return date(data.year + total // 12, total % 12 + 1, min(data.day, 28))


def _tramitacao(rng, pid, envio, hoje):
    """Eventos das 8 etapas a partir do envio, parando no que ainda não aconteceu.

    Devolve (eventos, datas de conclusão por etapa).
    """
    eventos, concluidas = [], {}
    data = envio
    for etapa in ind.ETAPAS:
        num = etapa['num']
        eventos.append(EventoEtapaMock(pid, num, ind.ENTRADA, data))
        # Duração líquida em torno de 80% do prazo, com cauda longa.
        duracao = max(1, round(etapa['prazo'] * rng.lognormvariate(-0.25, 0.55)))
        if rng.random() < CHANCE_DEVOLUCAO[num - 1]:
            devolucao = _somar_uteis(data, max(1, duracao // 2))
            if devolucao > hoje:
                break
            motivo = MOTIVO_POR_ETAPA[num] if rng.random() < .6 else rng.choice(ind.MOTIVOS_DEVOLUCAO)
            previsao = _somar_uteis(devolucao, etapa['retorno'])
            eventos.append(EventoEtapaMock(pid, num, ind.DEVOLUCAO, devolucao, motivo, previsao))
            if rng.random() < CHANCE_INATIVACAO:
                inativacao = _somar_uteis(previsao, 20)
                if inativacao <= hoje:
                    eventos.append(EventoEtapaMock(pid, num, ind.INATIVACAO, inativacao))
                break
            reenvio = _somar_uteis(devolucao, max(1, round(etapa['retorno'] * rng.uniform(.4, 1.6))))
            if reenvio > hoje:
                break
            eventos.append(EventoEtapaMock(pid, num, ind.REENVIO, reenvio))
            data = reenvio
            duracao = max(1, duracao - duracao // 2)
        conclusao = _somar_uteis(data, duracao)
        if conclusao > hoje:
            break
        eventos.append(EventoEtapaMock(pid, num, ind.CONCLUSAO, conclusao))
        concluidas[num] = conclusao
        data = conclusao
    return eventos, concluidas


def _orcamento(rng, projeto):
    """Itens de orçamento coerentes com o tipo de estudo."""
    patrocinado = projeto.tipo_pesq == 'Ensaio clínico' and rng.random() < .6
    fomentado = projeto.tipo_fomento in ('EDITAL DE AGÊNCIAS DE FOMENTO', 'PÚBLICO NACIONAL')
    itens = []
    for _ in range(rng.randint(1, 5)):
        rubrica = rng.choices(
            ind.RUBRICAS[:8], weights=[30, 22, 10, 10, 6, 14, 5, 3]
        )[0]
        if patrocinado:
            fonte = 'Patrocinador'
        elif rubrica in ('Exames e procedimentos', 'Material de consumo') and rng.random() < .45:
            fonte = ind.FONTE_HU
        elif fomentado:
            fonte = 'Fomento'
        else:
            fonte = rng.choice(['Recurso próprio da equipe', 'Instituição de ensino ou pesquisa', 'Fomento'])
        teto = 60 if rubrica in ('Pessoal e bolsas', 'Equipamentos e material permanente') else 18
        itens.append(ItemOrcamentoMock(projeto.sig_id_projeto, rubrica, fonte, Decimal(rng.randint(1, teto) * 1000)))
    if patrocinado:
        itens.append(ItemOrcamentoMock(
            projeto.sig_id_projeto, ind.RUBRICA_RESSARCIMENTO, 'Patrocinador', Decimal(rng.randint(5, 40) * 1000)
        ))
    return itens


def _relatorios(rng, projeto, hoje):
    """Relatórios semestrais (parciais) e o final, com situação conforme o prazo."""
    rels = []
    limite = hoje + timedelta(days=60)
    inicio_periodo = projeto.inicio_coleta
    while True:
        fim_periodo = _somar_meses(inicio_periodo, 6)
        final = projeto.fim_coleta and fim_periodo >= projeto.fim_coleta
        if final:
            fim_periodo = projeto.fim_coleta
        prazo = fim_periodo + timedelta(days=30)
        if prazo > limite:
            break
        periodo = f'{inicio_periodo:%m/%Y} a {fim_periodo:%m/%Y}'
        rel = RelatorioMock(projeto.sig_id_projeto, 'Final' if final else 'Parcial', periodo, prazo, ind.REL_PENDENTE)
        entregue = (
            prazo < hoje - timedelta(days=45)
            or (prazo < hoje and rng.random() < .75)
            or rng.random() < .15
        )
        if entregue:
            entrega = prazo + timedelta(days=rng.choice([-12, -6, -3, -1, 0, 2, 9]))
            if entrega <= hoje:
                rel.entregue_em = entrega
                analise = _somar_uteis(entrega, rng.randint(1, 9))
                if analise <= hoje and rng.random() < .9:
                    rel.situacao, rel.aceito_em = ind.REL_ACEITO, analise
                elif analise <= hoje and rng.random() < .5:
                    rel.situacao = ind.REL_DEVOLVIDO
                    rel.prazo = _somar_uteis(analise, 5)
                else:
                    rel.situacao = ind.REL_ENTREGUE
        rels.append(rel)
        if final:
            break
        inicio_periodo = fim_periodo
    return rels


@lru_cache(maxsize=4)
def _gerar(hoje):
    rng = random.Random(SEMENTE)
    projetos, eventos, itens, relatorios = [], [], [], []
    for i in range(1, QUANTIDADE_PROJETOS + 1):
        # Envios nos últimos ~4 anos, mais densos nos meses recentes; uma parte
        # bem recente para haver estudos ainda em tramitação.
        if rng.random() < .2:
            envio = hoje - timedelta(days=rng.randint(3, 80))
        else:
            envio = hoje - timedelta(days=int(rng.triangular(5, 4 * 365, 120)))
        pid = f'HU-{i:04d}/{envio.year}'
        tipo = _escolher(rng, TIPOS)
        multicentrico = rng.random() < .1
        evs, concluidas = _tramitacao(rng, pid, envio, hoje)
        eventos.extend(evs)

        aprovacao = concluidas.get(ind.ETAPA_APROVACAO)
        inicio = None
        if ind.ETAPA_INICIO in concluidas:
            inicio = concluidas[ind.ETAPA_INICIO] + timedelta(days=rng.randint(0, 20))
            inicio = inicio if inicio <= hoje else None
        tema = rng.choice(TEMAS)
        projeto = ProjetoMock(
            sig_id_projeto=pid,
            titulo=f'{tema[0].upper()}{tema[1:]} ({i})',
            tipo_pesq=tipo,
            tipo_fomento=_escolher(rng, FOMENTOS),
            multicentrico=multicentrico,
            desenvolvimento_tecnologico=(
                'sim' if tipo == 'Desenvolvimento tecnológico' or rng.random() < .06 else 'nao'
            ),
            parceria_HUB_UNB=rng.random() < .6,
            com_outro_hu=rng.random() < (.5 if multicentrico else .03),
            linhas_pesq='; '.join(rng.sample(LINHAS, rng.choice([1, 1, 2]))),
            especialidade_proponente=rng.choice(LINHAS),
            classificacoes=[_escolher(rng, CLASSIFICACOES)],
            data_aprovacao_inst=aprovacao,
            inicio_coleta=inicio,
            fim_coleta=_somar_meses(inicio, rng.randint(6, 30)) if inicio else None,
            parecer_cep=(
                ('na' if tipo == 'Dados secundários' and rng.random() < .4 else 'sim')
                if ind.ETAPA_CEP in concluidas else None
            ),
            coordenacao=rng.choice(COORDENACAO),
            vinculos=rng.sample(list(VINCULOS), rng.randint(2, 4)),
        )
        projetos.append(projeto)
        if rng.random() < .75:
            itens.extend(_orcamento(rng, projeto))
        if projeto.inicio_coleta:
            relatorios.extend(_relatorios(rng, projeto, hoje))
    return DadosDashboard(projetos, eventos, itens, relatorios)


def carregar(hoje=None):
    """Dados de exemplo para a data informada (padrão: hoje)."""
    return _gerar(hoje or date.today())
