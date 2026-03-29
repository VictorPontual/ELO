from django.db import models
from contas.models import Pesquisador

class Unidade(models.Model):
    nome_unidade = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.nome_unidade

class Projeto(models.Model):
    sig_id_projeto = models.CharField(max_length=100, primary_key=True)
    sig_id_pesq = models.CharField(max_length=100, blank=True, null=True)
    data_ent_sig = models.DateField(blank=True, null=True)
    data_lib_analise = models.DateField(blank=True, null=True)
    titulo = models.CharField(max_length=255)
    class_inst = models.CharField(max_length=100, blank=True, null=True)
    tipo_pesq = models.CharField(max_length=100, blank=True, null=True)
    desenvolvimento_tecnologico = models.BooleanField(default=False)
    multicentrico = models.BooleanField(default=False)
    especialidade_proponente = models.CharField(max_length=100, blank=True, null=True)
    linhas_pesq = models.TextField(blank=True, null=True)
    inicio_coleta = models.DateField(blank=True, null=True)
    fim_coleta = models.DateField(blank=True, null=True)
    data_aprovacao_inst = models.DateField(blank=True, null=True)
    parecer_cep = models.CharField(max_length=100, blank=True, null=True)
    data_parecer_cep = models.DateField(blank=True, null=True)
    papel_HUB_multi = models.CharField(max_length=100, blank=True, null=True)
    parceria_HUB_UNB = models.BooleanField(default=False)
    HUB_proponente = models.BooleanField(default=False)
    
    pesquisadores = models.ManyToManyField(Pesquisador, through='Participacao')
    unidades = models.ManyToManyField(Unidade, through='Envolve')

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
    atividade = models.CharField(max_length=255)

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