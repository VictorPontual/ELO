from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contas', '0017_pesquisador_preferencia_comunicacao'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pesquisador',
            name='numero_rede_pesquisa',
        ),
    ]
