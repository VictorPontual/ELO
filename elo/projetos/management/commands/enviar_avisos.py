"""Comando agendável que envia os avisos periódicos aos líderes dos projetos.

Uso típico (agendado via Task Scheduler do Windows ou cron):

    python manage.py enviar_avisos

Um projeto recebe novo aviso quando o último aviso registrado foi há mais de
`intervalo_dias` (configurado em ConfiguracaoAviso) ou quando nunca houve aviso.

Opções:
    --force          ignora o intervalo e a flag "ativo" e envia para todos os projetos.
    --projeto SIG_ID envia apenas para o projeto informado.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from projetos.models import AvisoEnviado, ConfiguracaoAviso, Projeto
from projetos.notificacoes import enviar_aviso_para_lider, obter_lider


class Command(BaseCommand):
    help = 'Envia avisos periódicos aos líderes dos projetos conforme a configuração global.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Ignora o intervalo e a flag "ativo" e envia para todos os projetos elegíveis.',
        )
        parser.add_argument(
            '--projeto',
            type=str,
            dest='projeto',
            help='Envia apenas para o projeto com este SIG ID.',
        )

    def handle(self, *args, **options):
        config = ConfiguracaoAviso.carregar()
        forcar = options['force']

        if not config.ativo and not forcar:
            self.stdout.write(self.style.WARNING(
                'Envio de avisos desativado na configuração. Use --force para ignorar.'
            ))
            return

        projetos = Projeto.objects.all()
        if options.get('projeto'):
            projetos = projetos.filter(sig_id_projeto=options['projeto'])

        limite = timezone.now() - timedelta(days=config.intervalo_dias)
        total_sucesso = 0
        total_falha = 0
        projetos_processados = 0

        for projeto in projetos:
            if obter_lider(projeto) is None:
                continue

            if not forcar:
                ultimo = (
                    AvisoEnviado.objects
                    .filter(projeto=projeto)
                    .order_by('-data_envio')
                    .first()
                )
                if ultimo and ultimo.data_envio > limite:
                    continue

            registros = enviar_aviso_para_lider(projeto, config)
            if not registros:
                self.stdout.write(self.style.WARNING(
                    f'{projeto.sig_id_projeto}: líder sem preferência de comunicação definida.'
                ))
                continue

            projetos_processados += 1
            for registro in registros:
                status = 'OK' if registro.sucesso else 'FALHA'
                estilo = self.style.SUCCESS if registro.sucesso else self.style.ERROR
                self.stdout.write(estilo(
                    f'[{status}] {projeto.sig_id_projeto} -> {registro.pesquisador} '
                    f'({registro.canal}): {registro.detalhe}'
                ))
                if registro.sucesso:
                    total_sucesso += 1
                else:
                    total_falha += 1

        self.stdout.write(self.style.SUCCESS(
            f'Concluído. Projetos com aviso: {projetos_processados} | '
            f'Envios com sucesso: {total_sucesso} | Falhas: {total_falha}.'
        ))
