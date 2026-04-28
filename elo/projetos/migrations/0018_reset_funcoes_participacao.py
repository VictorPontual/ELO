from django.db import migrations


def reset_funcoes_participacao(apps, schema_editor):
    FuncaoPesquisador = apps.get_model('projetos', 'FuncaoPesquisador')
    Participacao = apps.get_model('projetos', 'Participacao')

    novas_funcoes = [
        'Pesquisador principal',
        'Sub-investigador',
        'Coordenador',
        'Equipe de pesquisa',
    ]

    Participacao.objects.update(funcao=None)
    FuncaoPesquisador.objects.exclude(nome_funcao__in=novas_funcoes).delete()

    for nome in novas_funcoes:
        FuncaoPesquisador.objects.get_or_create(nome_funcao=nome)


class Migration(migrations.Migration):

    dependencies = [
        ('projetos', '0017_participacao_vinculo_funcao'),
    ]

    operations = [
        migrations.RunPython(reset_funcoes_participacao, migrations.RunPython.noop),
    ]