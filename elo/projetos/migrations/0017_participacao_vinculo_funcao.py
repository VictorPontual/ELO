from django.db import migrations, models
import django.db.models.deletion


def migrar_atividade_para_funcao(apps, schema_editor):
    Participacao = apps.get_model('projetos', 'Participacao')
    FuncaoPesquisador = apps.get_model('projetos', 'FuncaoPesquisador')

    atividades = (
        Participacao.objects.exclude(atividade__isnull=True)
        .exclude(atividade__exact='')
        .values_list('atividade', flat=True)
        .distinct()
    )

    for atividade in atividades:
        FuncaoPesquisador.objects.get_or_create(nome_funcao=atividade)

    for participacao in Participacao.objects.exclude(atividade__isnull=True).exclude(atividade__exact=''):
        funcao = FuncaoPesquisador.objects.filter(nome_funcao=participacao.atividade).first()
        if funcao:
            participacao.funcao = funcao
            participacao.save(update_fields=['funcao'])


class Migration(migrations.Migration):

    dependencies = [
        ('projetos', '0016_alter_projeto_formalizacao_instrumento'),
    ]

    operations = [
        migrations.CreateModel(
            name='FuncaoPesquisador',
            fields=[
                ('nome_funcao', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Função do Pesquisador',
                'verbose_name_plural': 'Funções do Pesquisador',
            },
        ),
        migrations.CreateModel(
            name='VinculoPesquisador',
            fields=[
                ('nome_vinculo', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Vínculo do Pesquisador',
                'verbose_name_plural': 'Vínculos do Pesquisador',
            },
        ),
        migrations.AddField(
            model_name='participacao',
            name='funcao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='projetos.funcaopesquisador'),
        ),
        migrations.AddField(
            model_name='participacao',
            name='vinculo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='projetos.vinculopesquisador'),
        ),
        migrations.RunPython(migrar_atividade_para_funcao, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='participacao',
            name='atividade',
        ),
    ]