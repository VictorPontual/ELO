"""Formatação dos números exibidos nos dashboards (padrão brasileiro)."""

from django import template

register = template.Library()

VAZIO = '—'


def _milhar(valor):
    return f'{valor:,.0f}'.replace(',', '.')


def _decimal(valor):
    """Inteiro sem casas; fracionário com uma casa e vírgula."""
    if float(valor).is_integer():
        return _milhar(valor)
    return f'{valor:.1f}'.replace('.', ',')


@register.filter
def brl(valor):
    if valor is None:
        return VAZIO
    sinal = '−' if valor < 0 else ''
    return f'{sinal}R$ {_milhar(abs(valor))}'


@register.filter
def dias(valor):
    return VAZIO if valor is None else f'{_decimal(valor)} d'


@register.filter
def pct(valor):
    return VAZIO if valor is None else f'{valor}%'


@register.filter
def num(valor):
    return VAZIO if valor is None else _decimal(valor)
