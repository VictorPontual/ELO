from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contas', '0002_pesquisador_numero_rede_pesquisa'),
    ]

    operations = [
        migrations.AddField(
            model_name='pesquisador',
            name='preferencia_comunicacao',
            field=models.BooleanField(default=False),
        ),
    ]