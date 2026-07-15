from django.db import models
from contas.models import Pesquisador

class Unidade(models.Model):
    nome_unidade = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.nome_unidade

class ClassificacaoInstitucional(models.Model):
    nome_classificacao = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.nome_classificacao
    
    class Meta:
        verbose_name = 'Classificação Institucional'
        verbose_name_plural = 'Classificações Institucionais'


class TipoPesquisa(models.Model):
    nome_tipo = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.nome_tipo

    class Meta:
        verbose_name = 'Tipo de Pesquisa'
        verbose_name_plural = 'Tipos de Pesquisa'


class SubTipoPesquisa(models.Model):
    nome_sub_tipo = models.CharField(max_length=255)
    tipo = models.ForeignKey(TipoPesquisa, on_delete=models.CASCADE, related_name='subtipos')

    def __str__(self):
        return self.nome_sub_tipo

    class Meta:
        unique_together = ('nome_sub_tipo', 'tipo')
        verbose_name = 'Sub-tipo de Pesquisa'
        verbose_name_plural = 'Sub-tipos de Pesquisa'


class LinhaPesquisa(models.Model):
    nome_linha = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.nome_linha

    class Meta:
        verbose_name = 'Linha de Pesquisa'
        verbose_name_plural = 'Linhas de Pesquisa'


class EspecialidadeProponente(models.Model):
    nome_especialidade = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.nome_especialidade

    class Meta:
        verbose_name = 'Especialidade do Proponente'
        verbose_name_plural = 'Especialidades do Proponente'


class InstituicaoProponente(models.Model):
    nome_instituicao = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.nome_instituicao

    class Meta:
        verbose_name = 'Instituição Proponente'
        verbose_name_plural = 'Instituições Proponentes'


class ProvedorFomento(models.Model):
    nome_provedor = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.nome_provedor

    class Meta:
        verbose_name = 'Provedor de Fomento'
        verbose_name_plural = 'Provedores de Fomento'


class HospitalHubBrasil(models.Model):
    nome_hospital = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.nome_hospital

    class Meta:
        verbose_name = 'Hospital da Rede HUBrasil'
        verbose_name_plural = 'Hospitais da Rede HUBrasil'


class VinculoPesquisador(models.Model):
    nome_vinculo = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.nome_vinculo

    class Meta:
        verbose_name = 'Vínculo do Pesquisador'
        verbose_name_plural = 'Vínculos do Pesquisador'


class FuncaoPesquisador(models.Model):
    nome_funcao = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.nome_funcao

    class Meta:
        verbose_name = 'Função do Pesquisador'
        verbose_name_plural = 'Funções do Pesquisador'

class Projeto(models.Model):
    DESENVOLVIMENTO_TECNOLOGICO_CHOICES = [
        ('sim', 'Sim'),
        ('nao', 'Não'),
        ('duvida', 'Em dúvida'),
    ]

    PARECER_CEP_CHOICES = [
        ('sim', 'Sim'),
        ('na', 'N/A'),
    ]

    TIPO_FOMENTO_CHOICES = [
        ('EDITAL DE AGÊNCIAS DE FOMENTO', 'EDITAL DE AGÊNCIAS DE FOMENTO'),
        ('PÚBLICO NACIONAL', 'PÚBLICO NACIONAL'),
        ('PÚBLICO INTERNACIONAL', 'PÚBLICO INTERNACIONAL'),
        ('PRIVADO INTERNACIONAL', 'PRIVADO INTERNACIONAL'),
        ('PRIVADO NACIONAL', 'PRIVADO NACIONAL'),
        ('PRÓPRIO PESQUISADOR', 'PRÓPRIO PESQUISADOR'),
        ('OUTRA', 'OUTRA'),
    ]

    PAPEL_HUB_CHOICES = [
        ('coordenador', 'Coordenador'),
        ('coparticipante', 'Coparticipante'),
        ('participante', 'Participante'),
    ]

    sig_id_projeto = models.CharField(max_length=100, primary_key=True)
    sig_id_pesq = models.CharField(max_length=100, blank=True, null=True)
    data_ent_sig = models.DateField(blank=True, null=True)
    data_lib_analise = models.DateField(blank=True, null=True)
    titulo = models.CharField(max_length=255)
    tipo_pesq = models.CharField(max_length=255, blank=True, null=True)
    sub_tipo_pesq = models.CharField(max_length=255, blank=True, null=True)
    desenvolvimento_tecnologico = models.CharField(
        max_length=10,
        choices=DESENVOLVIMENTO_TECNOLOGICO_CHOICES,
        blank=True,
        null=True,
    )
    multicentrico = models.BooleanField(default=False)
    especialidade_proponente = models.CharField(max_length=255, blank=True, null=True)
    instituicao_proponente = models.CharField(max_length=255, blank=True, null=True)
    tipo_fomento = models.CharField(max_length=50, choices=TIPO_FOMENTO_CHOICES, blank=True, null=True)
    provedor_fomento = models.CharField(max_length=255, blank=True, null=True)
    formalizacao_instrumento = models.BooleanField(default=False)
    linhas_pesq = models.TextField(blank=True, null=True)
    inicio_coleta = models.DateField(blank=True, null=True)
    fim_coleta = models.DateField(blank=True, null=True)
    data_aprovacao_inst = models.DateField(blank=True, null=True)
    parecer_cep = models.CharField(max_length=10, choices=PARECER_CEP_CHOICES, blank=True, null=True)
    data_parecer_cep = models.DateField(blank=True, null=True)
    papel_HUB_multi = models.CharField(
        max_length=100,
        choices=PAPEL_HUB_CHOICES,
        blank=True,
        null=True,
    )
    parceria_HUB_UNB = models.BooleanField(default=False)
    HUB_proponente = models.BooleanField(default=False)
    
    pesquisadores = models.ManyToManyField(Pesquisador, through='Participacao')
    unidades = models.ManyToManyField(Unidade, through='Envolve')
    hospitais_parceiros = models.ManyToManyField(HospitalHubBrasil, through='ParceriaHospital', blank=True)
    classificacoes = models.ManyToManyField(ClassificacaoInstitucional, blank=True)

    def __str__(self):
        return self.titulo



class Fomento(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='fomentos')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    fonte = models.CharField(max_length=100)
    tipo_fonte = models.CharField(max_length=100, blank=True, null=True)
    tipo_valor = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Fomento de {self.fonte} para {self.projeto.titulo}"

class Participacao(models.Model):
    pesquisador = models.ForeignKey(Pesquisador, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    vinculo = models.ForeignKey(VinculoPesquisador, on_delete=models.SET_NULL, blank=True, null=True)
    funcao = models.ForeignKey(FuncaoPesquisador, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        unique_together = ('pesquisador', 'projeto')

    def __str__(self):
        return f"{self.pesquisador.user.username} participa em {self.projeto.titulo}"

class Envolve(models.Model):
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('unidade', 'projeto')

    def __str__(self):
        return f"{self.unidade.nome_unidade} envolvida em {self.projeto.titulo}"


class ParceriaHospital(models.Model):
    hospital = models.ForeignKey(HospitalHubBrasil, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('hospital', 'projeto')

    def __str__(self):
        return f"{self.hospital.nome_hospital} parceiro em {self.projeto.titulo}"


class ConfiguracaoAviso(models.Model):
    """Configuração global (única) do aviso periódico enviado aos líderes dos projetos."""

    MENSAGEM_PADRAO = (
        'Olá {nome},\n\n'
        'Este é um aviso periódico referente ao seu projeto de pesquisa '
        '"{titulo}" (SIG {sig_id}).\n\n'
        'Por favor, mantenha as informações do projeto atualizadas no sistema ELO.\n\n'
        'Atenciosamente,\n'
        'Equipe de Gestão da Pesquisa'
    )

    assunto = models.CharField(
        max_length=255,
        default='Aviso sobre seu projeto de pesquisa',
    )
    mensagem = models.TextField(default=MENSAGEM_PADRAO)
    intervalo_dias = models.PositiveIntegerField(default=30)
    ativo = models.BooleanField(default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração de Aviso'
        verbose_name_plural = 'Configuração de Avisos'

    def __str__(self):
        return 'Configuração de Avisos'

    def save(self, *args, **kwargs):
        # Singleton: sempre o mesmo registro
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def carregar(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ConfiguracaoAlertas(models.Model):
    """Configuração global (única) dos alertas de CEP e relatório na Main page."""

    ASSUNTO_CEP_PADRAO = 'Pendência: parecer do CEP do seu projeto de pesquisa'
    MENSAGEM_CEP_PADRAO = (
        'Olá {nome},\n\n'
        'O projeto "{titulo}" (SIG {sig_id}) foi aprovado institucionalmente em '
        '{data_aprovacao} e ainda não possui parecer do CEP registrado.\n\n'
        'O parecer do CEP é esperado em até {prazo_cep} meses após a aprovação '
        'institucional. Por favor, providencie a submissão/registro do parecer.\n\n'
        'Atenciosamente,\nEquipe de Gestão da Pesquisa'
    )
    ASSUNTO_RELATORIO_PADRAO = 'Pendência: relatório do seu projeto de pesquisa'
    MENSAGEM_RELATORIO_PADRAO = (
        'Olá {nome},\n\n'
        'Passou-se mais de {prazo_relatorio} meses desde o parecer do CEP do '
        'projeto "{titulo}" (SIG {sig_id}), emitido em {data_parecer_cep}.\n\n'
        'É necessário apresentar o relatório do projeto. Por favor, providencie '
        'o envio.\n\nAtenciosamente,\nEquipe de Gestão da Pesquisa'
    )

    cep_ativo = models.BooleanField(default=True, verbose_name='Alerta de CEP ativo')
    prazo_cep_meses = models.PositiveIntegerField(
        default=6,
        verbose_name='Prazo para parecer do CEP (meses após aprovação institucional)',
    )
    assunto_cep = models.CharField(max_length=255, default=ASSUNTO_CEP_PADRAO)
    mensagem_cep = models.TextField(default=MENSAGEM_CEP_PADRAO)

    relatorio_ativo = models.BooleanField(default=True, verbose_name='Alerta de relatório ativo')
    prazo_relatorio_meses = models.PositiveIntegerField(
        default=12,
        verbose_name='Prazo para relatório (meses após parecer do CEP)',
    )
    assunto_relatorio = models.CharField(max_length=255, default=ASSUNTO_RELATORIO_PADRAO)
    mensagem_relatorio = models.TextField(default=MENSAGEM_RELATORIO_PADRAO)

    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração de Alertas'
        verbose_name_plural = 'Configuração de Alertas'

    def __str__(self):
        return 'Configuração de Alertas'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def carregar(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class TipoAviso(models.Model):
    """Tipo de aviso geral cadastrável, gerenciado na página de avisos."""

    nome = models.CharField(max_length=120, unique=True)
    assunto = models.CharField(max_length=255)
    mensagem = models.TextField(
        help_text='Variáveis disponíveis: {nome}, {titulo}, {sig_id}.'
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Tipo de Aviso'
        verbose_name_plural = 'Tipos de Aviso'

    def __str__(self):
        return self.nome


class AvisoEnviado(models.Model):
    """Registro de cada aviso enviado (ou tentado) a um pesquisador de um projeto."""

    CANAL_CHOICES = [
        ('email', 'E-mail'),
        ('whatsapp', 'WhatsApp'),
    ]

    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='avisos')
    pesquisador = models.ForeignKey(Pesquisador, on_delete=models.CASCADE)
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES)
    destino = models.CharField(max_length=255, blank=True)
    assunto = models.CharField(max_length=255, blank=True)
    mensagem = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)
    sucesso = models.BooleanField(default=False)
    detalhe = models.TextField(blank=True)

    class Meta:
        ordering = ['-data_envio']
        verbose_name = 'Aviso Enviado'
        verbose_name_plural = 'Avisos Enviados'

    def __str__(self):
        return f'Aviso para {self.pesquisador} em {self.data_envio:%d/%m/%Y %H:%M}'