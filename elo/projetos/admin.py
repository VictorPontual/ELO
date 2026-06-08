from django.contrib import admin

from .models import ConfiguracaoAviso, AvisoEnviado


@admin.register(ConfiguracaoAviso)
class ConfiguracaoAvisoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'intervalo_dias', 'ativo', 'atualizado_em')


@admin.register(AvisoEnviado)
class AvisoEnviadoAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'pesquisador', 'canal', 'sucesso', 'data_envio')
    list_filter = ('canal', 'sucesso', 'data_envio')
    search_fields = ('projeto__sig_id_projeto', 'projeto__titulo')
    readonly_fields = ('data_envio',)
