from django.db import migrations


def limpar_papel_hub_invalidos(apps, schema_editor):
    Projeto = apps.get_model('projetos', 'Projeto')
    escolhas = {'coordenador', 'coparticipante', 'participante'}

    for projeto in Projeto.objects.exclude(papel_HUB_multi__isnull=True).exclude(papel_HUB_multi__exact=''):
        if projeto.papel_HUB_multi not in escolhas:
            projeto.papel_HUB_multi = None
            projeto.save(update_fields=['papel_HUB_multi'])


class Migration(migrations.Migration):

    dependencies = [
        ('projetos', '0018_reset_funcoes_participacao'),
    ]

    operations = [
        migrations.RunPython(limpar_papel_hub_invalidos, migrations.RunPython.noop),
    ]