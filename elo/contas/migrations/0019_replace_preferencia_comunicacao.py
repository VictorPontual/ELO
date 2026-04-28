from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contas', '0018_remove_pesquisador_numero_rede_pesquisa'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pesquisador',
            name='preferencia_comunicacao',
        ),
        migrations.AddField(
            model_name='pesquisador',
            name='preferencia_comunicacao_celular',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pesquisador',
            name='preferencia_comunicacao_email',
            field=models.BooleanField(default=False),
        ),
    ]
