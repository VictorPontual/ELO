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