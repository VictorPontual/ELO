from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('projetos', '0019_papel_hub_choices'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinhaPesquisa',
            fields=[
                ('nome_linha', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Linha de Pesquisa',
                'verbose_name_plural': 'Linhas de Pesquisa',
            },
        ),
    ]
