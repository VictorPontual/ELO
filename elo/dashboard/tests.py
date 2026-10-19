from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from . import dados_mock, indicadores as ind
from .dados_mock import EventoEtapaMock as Ev, ItemOrcamentoMock, ProjetoMock, RelatorioMock
from .templatetags.dashboard_extras import brl, dias

HOJE = date(2026, 10, 19)  # segunda-feira


def _projeto(sig, **campos):
    padrao = dict(
        titulo=f'Projeto {sig}', tipo_pesq='Observacional', tipo_fomento=None,
        multicentrico=False, desenvolvimento_tecnologico='nao', parceria_HUB_UNB=False,
        com_outro_hu=False, linhas_pesq='', especialidade_proponente='Oncologia',
    )
    padrao.update(campos)
    return ProjetoMock(sig_id_projeto=sig, **padrao)


class UtilitariosTests(SimpleTestCase):
    def test_dias_uteis_ignora_fim_de_semana(self):
        # sexta -> segunda: só a segunda conta
        self.assertEqual(ind.dias_uteis(date(2026, 10, 16), date(2026, 10, 19)), 1)
        # segunda -> segunda seguinte: 5 dias úteis
        self.assertEqual(ind.dias_uteis(date(2026, 10, 12), date(2026, 10, 19)), 5)
        self.assertEqual(ind.dias_uteis(date(2026, 10, 19), date(2026, 10, 19)), 0)
        self.assertEqual(ind.dias_uteis(None, date(2026, 10, 19)), 0)

    def test_mediana_e_percentil(self):
        self.assertEqual(ind.mediana([1, 2, 3, 10]), 2.5)
        self.assertIsNone(ind.mediana([]))
        self.assertEqual(ind.percentil(list(range(1, 11)), 90), 9)
        self.assertIsNone(ind.percentil([], 90))

    def test_filtros_de_formatacao(self):
        self.assertEqual(brl(Decimal('1234567.4')), 'R$ 1.234.567')
        self.assertEqual(brl(Decimal('-28000')), '−R$ 28.000')
        self.assertEqual(brl(None), '—')
        self.assertEqual(dias(2.5), '2,5 d')
        self.assertEqual(dias(4), '4 d')


class PainelTests(SimpleTestCase):
    def setUp(self):
        self.projetos = [
            _projeto('A', data_aprovacao_inst=date(2026, 2, 10), multicentrico=True,
                     tipo_pesq='Ensaio clínico', desenvolvimento_tecnologico='sim',
                     inicio_coleta=date(2026, 3, 1), classificacoes=['Acadêmica']),
            _projeto('B', data_aprovacao_inst=date(2026, 8, 5), linhas_pesq='Oncologia; Cardiologia'),
            _projeto('C', data_aprovacao_inst=date(2025, 5, 1), inicio_coleta=date(2025, 6, 1),
                     fim_coleta=date(2026, 1, 1)),
            _projeto('D'),
            _projeto('E'),
        ]
        self.eventos = [Ev('E', 2, ind.INATIVACAO, date(2026, 9, 1))]

    def test_kpis_e_periodo(self):
        dados = ind.painel(self.projetos, self.eventos, 2026, HOJE)
        self.assertEqual(dados['kpis']['aprovados_acumulado'], 3)
        self.assertEqual(dados['kpis']['primeiro_ano'], 2025)
        self.assertEqual(dados['kpis']['aprovados_ano'], 2)
        self.assertEqual(dados['kpis']['multicentricos'], 1)
        self.assertEqual(dados['kpis']['tecnologicos'], 1)
        self.assertEqual(dados['kpis']['em_andamento'], 1)
        self.assertEqual(dados['periodo']['anos']['2026']['t'], [1, 0, 1, 0])
        self.assertEqual(dados['periodo']['anos']['2026']['b'], [1, 0, 0, 1, 0, 0])
        self.assertEqual(dados['periodo']['atual'], {'ano': '2026', 't': 3, 'b': 4})

    def test_pares_e_situacao(self):
        dados = ind.painel(self.projetos, self.eventos, 2026, HOJE)
        metodologia = dados['pares'][-1]
        self.assertEqual((metodologia['sim'], metodologia['nao']), (1, 1))
        situacao = dict(zip(dados['barras']['situacao']['labels'], dados['barras']['situacao']['values']))
        self.assertEqual(situacao, {
            'Concluídos': 1, 'Em andamento': 1, 'Aguardando início': 1,
            'Em tramitação': 1, 'Inativados': 1,
        })
        self.assertEqual(sorted(dados['barras']['linhas']['labels']), ['Cardiologia', 'Oncologia'])
        self.assertEqual(dados['barras']['classificacao']['labels'], ['Acadêmica'])


class TramitacaoTests(SimpleTestCase):
    def setUp(self):
        self.projetos = [_projeto('P1'), _projeto('P2', tipo_pesq='Qualitativo')]
        # Etapa 2: entra seg 05/10, devolvido qua 07/10 (2 d), reenvio seg 12/10
        # (previsão 14/10), conclui qua 14/10 (+2 d) => líquido 4 d úteis.
        self.eventos = [
            Ev('P1', 1, ind.ENTRADA, date(2026, 9, 28)),
            Ev('P1', 1, ind.CONCLUSAO, date(2026, 10, 5)),
            Ev('P1', 2, ind.ENTRADA, date(2026, 10, 5)),
            Ev('P1', 2, ind.DEVOLUCAO, date(2026, 10, 7), 'Documento ausente ou desatualizado',
               date(2026, 10, 14)),
            Ev('P1', 2, ind.REENVIO, date(2026, 10, 12)),
            Ev('P1', 2, ind.CONCLUSAO, date(2026, 10, 14)),
        ]
        for etapa in range(3, 9):
            self.eventos += [
                Ev('P1', etapa, ind.ENTRADA, date(2026, 10, 14)),
                Ev('P1', etapa, ind.CONCLUSAO, date(2026, 10, 16)),
            ]
        self.eventos += [
            Ev('P2', 2, ind.ENTRADA, date(2026, 10, 12)),
            Ev('P2', 2, ind.DEVOLUCAO, date(2026, 10, 13), 'Dado incoerente ou incompleto'),
        ]

    def test_tempo_por_etapa(self):
        dados = ind.tempo_por_etapa(self.projetos, self.eventos)
        etapa2 = dados['linhas'][1]
        self.assertEqual(etapa2['n'], 1)
        self.assertEqual(etapa2['mediana'], 4)
        self.assertEqual(etapa2['pct_prazo'], 100)
        self.assertEqual(etapa2['pct_devolvidos'], 100)  # P1 e P2 devolvidos
        self.assertEqual(dados['kpis']['concluidos'], 1)
        self.assertEqual(dados['kpis']['mediana_total'], 14)  # 28/09 -> 16/10
        self.assertEqual(dados['kpis']['mediana_retorno'], 3)  # 07/10 -> 12/10
        self.assertEqual(dados['kpis']['mediana_cep'], 2)

    def test_filtro_restringe_eventos(self):
        dados = ind.tempo_por_etapa(self.projetos[1:], self.eventos)
        self.assertEqual(dados['kpis']['concluidos'], 0)
        self.assertEqual(dados['linhas'][1]['pct_devolvidos'], 100)

    def test_mais_indicadores(self):
        dados = ind.mais_indicadores(self.projetos, self.eventos, [], HOJE)
        self.assertEqual(dados['kpis']['pct_primeira_passagem'], 0)
        self.assertEqual(dados['kpis']['pct_reenvio_prazo'], 100)
        self.assertEqual(dados['kpis']['devolvidos_agora'], 1)
        self.assertEqual(sorted(dados['motivos']['labels']), [
            'Dado incoerente ou incompleto', 'Documento ausente ou desatualizado',
        ])


class FinanceiroTests(SimpleTestCase):
    def test_totais(self):
        projetos = [_projeto('F1', tipo_pesq='Ensaio clínico'), _projeto('F2'), _projeto('F3')]
        itens = [
            ItemOrcamentoMock('F1', 'Pessoal e bolsas', 'Fomento', Decimal('100000')),
            ItemOrcamentoMock('F1', 'Exames e procedimentos', ind.FONTE_HU, Decimal('30000')),
            ItemOrcamentoMock('F1', ind.RUBRICA_RESSARCIMENTO, 'Patrocinador', Decimal('10000')),
            ItemOrcamentoMock('F2', 'Material de consumo', 'Recurso próprio da equipe', Decimal('5000')),
            ItemOrcamentoMock('OUTRO', 'Material de consumo', 'Fomento', Decimal('999')),
        ]
        dados = ind.financeiro(projetos, itens)
        kpis = dados['kpis']
        self.assertEqual(kpis['total'], Decimal('145000'))
        self.assertEqual(kpis['externos'], Decimal('110000'))
        self.assertEqual(kpis['custo_hu'], Decimal('30000'))
        self.assertEqual(kpis['ressarcimento'], Decimal('10000'))
        self.assertEqual(kpis['saldo_hu'], Decimal('-20000'))
        self.assertEqual(kpis['mediana_estudo'], Decimal('72500'))
        self.assertEqual((kpis['com_orcamento'], kpis['total_estudos']), (2, 3))
        self.assertEqual(dados['maiores'][0]['codigo'], 'F1')


class RelatoriosTests(SimpleTestCase):
    def setUp(self):
        self.projetos = [_projeto('R1', coordenacao='Ana Exemplo')]
        self.rels = [
            RelatorioMock('R1', 'Parcial', '', date(2026, 9, 25), ind.REL_PENDENTE),  # atrasado
            RelatorioMock('R1', 'Parcial', '', date(2026, 10, 26), ind.REL_PENDENTE),  # vence em breve
            RelatorioMock('R1', 'Parcial', '', date(2026, 10, 6), ind.REL_ENTREGUE, date(2026, 10, 6)),
            RelatorioMock('R1', 'Parcial', '', date(2026, 7, 14), ind.REL_ACEITO,
                          date(2026, 7, 16), date(2026, 7, 20)),
        ]

    def test_kpis(self):
        kpis = ind.relatorios(self.projetos, self.rels, HOJE)['kpis']
        self.assertEqual(kpis['a_entregar'], 2)
        self.assertEqual(kpis['em_atraso'], 1)
        self.assertEqual(kpis['vencem_em_breve'], 1)
        self.assertEqual(kpis['aguardando_analise'], 1)
        self.assertEqual(kpis['pct_no_prazo'], 50)
        self.assertEqual(kpis['mediana_analise'], 2)

    def test_filtro_e_ordem(self):
        dados = ind.relatorios(self.projetos, self.rels, HOJE, 'todos')
        self.assertEqual(dados['linhas'][0]['situacao'], 'Em atraso')
        self.assertEqual(dados['linhas'][0]['coordenacao'], 'Ana Exemplo')
        self.assertEqual(len(ind.relatorios(self.projetos, self.rels, HOJE, 'atraso')['linhas']), 1)
        self.assertEqual(ind.relatorios(self.projetos, self.rels, HOJE, 'xyz')['filtro'], 'todos')


class DadosMockTests(SimpleTestCase):
    def test_deterministico_e_coerente(self):
        a = dados_mock._gerar(HOJE)
        dados_mock._gerar.cache_clear()
        b = dados_mock._gerar(HOJE)
        self.assertEqual(a, b)
        self.assertEqual(len(a.projetos), dados_mock.QUANTIDADE_PROJETOS)
        ids = {p.sig_id_projeto for p in a.projetos}
        for colecao in (a.eventos, a.itens_orcamento, a.relatorios):
            self.assertTrue(colecao)
            self.assertTrue(all(o.projeto_id in ids for o in colecao))
        self.assertTrue(all(e.data <= HOJE for e in a.eventos))
        self.assertTrue(all(p.data_aprovacao_inst <= HOJE for p in a.projetos if p.data_aprovacao_inst))


class ViewsTests(TestCase):
    TELAS = ('dashboard', 'dashboard_mais', 'dashboard_tempo', 'dashboard_financeiro', 'dashboard_relatorios')

    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@exemplo.org', 'senha-teste-123')
        self.client.force_login(self.user)

    def test_todas_as_telas_abrem(self):
        for nome in self.TELAS:
            with self.subTest(nome=nome):
                self.assertEqual(self.client.get(reverse(nome)).status_code, 200)

    def test_filtros_por_querystring(self):
        self.assertEqual(self.client.get(reverse('dashboard'), {'ano': 'abc'}).status_code, 200)
        resposta = self.client.get(reverse('dashboard_tempo'), {'tipo': 'Observacional'})
        self.assertEqual(resposta.context['tipo_selecionado'], 'Observacional')
        resposta = self.client.get(reverse('dashboard_financeiro'), {'tipo': 'inexistente'})
        self.assertEqual(resposta.context['tipo_selecionado'], '')
        resposta = self.client.get(reverse('dashboard_relatorios'), {'situacao': 'atraso'})
        self.assertEqual(resposta.context['filtro'], 'atraso')

    def test_exige_login(self):
        self.client.logout()
        for nome in self.TELAS:
            with self.subTest(nome=nome):
                self.assertEqual(self.client.get(reverse(nome)).status_code, 302)
