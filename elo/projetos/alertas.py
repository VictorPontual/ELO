"""Cálculo dos alertas de CEP e relatório exibidos no quadrante da Main page.

Regras:
- CEP: projeto aprovado institucionalmente que, decorrido o prazo configurado
  (padrão 6 meses) desde a aprovação, ainda não tem parecer do CEP registrado.
- Relatório: projeto com parecer do CEP cujo prazo configurado (padrão 12 meses)
  desde o parecer já passou — relatório esperado.
"""

from calendar import monthrange
from datetime import date

from .models import ConfiguracaoAlertas


def adicionar_meses(data_base, meses):
    """Retorna data_base + `meses`, ajustando o dia para o fim do mês quando preciso."""
    total = data_base.month - 1 + meses
    ano = data_base.year + total // 12
    mes = total % 12 + 1
    dia = min(data_base.day, monthrange(ano, mes)[1])
    return date(ano, mes, dia)


def _tem_parecer_cep(projeto):
    return projeto.parecer_cep == 'sim' or projeto.data_parecer_cep is not None


def calcular_alertas(projetos, config=None, hoje=None):
    """Retorna a lista de alertas para os projetos informados.

    Cada alerta é um dict: {projeto, tipo, titulo, descricao, data_limite,
    dias_atraso}.
    """
    if config is None:
        config = ConfiguracaoAlertas.carregar()
    if hoje is None:
        hoje = date.today()

    alertas = []
    for projeto in projetos:
        # --- Alerta de parecer do CEP ---
        if (
            config.cep_ativo
            and projeto.data_aprovacao_inst
            and not _tem_parecer_cep(projeto)
        ):
            limite = adicionar_meses(projeto.data_aprovacao_inst, config.prazo_cep_meses)
            if hoje >= limite:
                alertas.append({
                    'projeto': projeto,
                    'tipo': 'cep',
                    'titulo': 'Parecer do CEP pendente',
                    'descricao': (
                        f'Aprovado institucionalmente em '
                        f'{projeto.data_aprovacao_inst.strftime("%d/%m/%Y")} e sem parecer '
                        f'do CEP há mais de {config.prazo_cep_meses} meses.'
                    ),
                    'data_limite': limite,
                    'dias_atraso': (hoje - limite).days,
                })

        # --- Alerta de relatório ---
        if config.relatorio_ativo and projeto.data_parecer_cep:
            limite = adicionar_meses(projeto.data_parecer_cep, config.prazo_relatorio_meses)
            if hoje >= limite:
                alertas.append({
                    'projeto': projeto,
                    'tipo': 'relatorio',
                    'titulo': 'Relatório pendente',
                    'descricao': (
                        f'Parecer do CEP em '
                        f'{projeto.data_parecer_cep.strftime("%d/%m/%Y")}; relatório esperado '
                        f'após {config.prazo_relatorio_meses} meses.'
                    ),
                    'data_limite': limite,
                    'dias_atraso': (hoje - limite).days,
                })

    # Mais atrasados primeiro.
    alertas.sort(key=lambda a: a['dias_atraso'], reverse=True)
    return alertas
