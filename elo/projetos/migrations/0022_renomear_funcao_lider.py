from django.db import migrations


def migrar_lider_para_principal(apps, schema_editor):
    FuncaoPesquisador = apps.get_model('projetos', 'FuncaoPesquisador')
    Participacao = apps.get_model('projetos', 'Participacao')

    lider = FuncaoPesquisador.objects.filter(nome_funcao='Líder').first()
    if not lider:
        return

    principal, _ = FuncaoPesquisador.objects.get_or_create(
        nome_funcao='Pesquisador principal'
    )
    Participacao.objects.filter(funcao=lider).update(funcao=principal)
    lider.delete()


def reverter(apps, schema_editor):
    # Não é possível distinguir com segurança quais eram 'Líder'; no-op.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('projetos', '0021_configuracaoaviso_alter_projeto_papel_hub_multi_and_more'),
    ]

    operations = [
        migrations.RunPython(migrar_lider_para_principal, reverter),
    ]
