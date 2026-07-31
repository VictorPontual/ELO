from django.db import migrations


# Preserva o comportamento atual: contas administrativas (is_staff, não
# superusuário) que já existiam passam a ter acesso "editar" nas áreas que
# podiam usar e "ver" no dashboard. O registro de ações continua exclusivo do
# superadmin (não é liberado aqui). Contas novas nascem sem acesso, para o
# superadmin liberar conscientemente.
AREAS_EDITAR = ['projetos', 'pesquisadores', 'avisos', 'ajustes']
AREA_VER = 'dashboard'


def seed(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    AcessoPagina = apps.get_model('contas', 'AcessoPagina')

    for user in User.objects.filter(is_staff=True, is_superuser=False):
        for area in AREAS_EDITAR:
            AcessoPagina.objects.get_or_create(
                user=user, area=area, defaults={'nivel': 'editar'}
            )
        AcessoPagina.objects.get_or_create(
            user=user, area=AREA_VER, defaults={'nivel': 'ver'}
        )


def unseed(apps, schema_editor):
    # Reversão: remove todos os acessos (a tabela é recriada do zero se preciso).
    AcessoPagina = apps.get_model('contas', 'AcessoPagina')
    AcessoPagina.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('contas', '0023_acessopagina'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
