from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pesquisador',
            name='numero_rede_pesquisa',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
