from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .models import Projeto, Participacao, Unidade, ClassificacaoInstitucional, TipoPesquisa, LinhaPesquisa, EspecialidadeProponente, InstituicaoProponente, HospitalHubBrasil, Envolve, ParceriaHospital, VinculoPesquisador, FuncaoPesquisador, ConfiguracaoAviso, AvisoEnviado
from .notificacoes import obter_lider
from contas.models import Pesquisador
from django import forms


TIPOS_PESQUISA_INICIAIS = [
    'Graduação (IC, PIT, TC)',
    'Pós Graduação latu senso (especialização e residência)',
    'Pós Graduação strictu senso (mestrado, doutorado e pós doc)',
    'Iniciativa de colaboradores',
    'Iniciativa de docentes',
    'pesquisa clínica patrocinada',
    'outros',
]

LINHAS_PESQUISA_INICIAIS = [
    'Doenças cardiovasculares',
    'Doenças do sistema nervoso',
    'Doenças em nefrologia',
    'Doenças em oncologia e onco-hematologia',
    'Doenças infecciosas e parasitárias',
    'Doenças inflamatórias e imunomediadas',
    'Doenças respiratórias',
    'Ensino em saúde',
    'Estudos em endocrinologia e transtornos do metabolismo',
    'Geriatria, gerontologia, envelhecimento e longevidade',
    'Saúde Bucal',
    'Saúde da mulher',
    'Saúde mental',
    'Transplante de órgãos, células e tecidos',
    'Outras',
]

ESPECIALIDADES_PROPONENTE_INICIAIS = [
    'Anestesiologia',
    'Arquivologia',
    'Biblioteconomia',
    'Cardiologia',
    'Ciências biológicas',
    'Cirurgia do aparelho digestivo',
    'Cirurgia geral',
    'Cirurgia oncológica',
    'Cirurgia pediátrica',
    'Cirurgia vascular',
    'Cirurgia videolaparoscópica',
    'Clínica médica',
    'Coloproctologia',
    'Dermatologia',
    'Doenças infecto parasitárias',
    'Endocrinologia',
    'Endocrinologia pediátrica',
    'Enfermagem',
    'Engenharia de energia ciência de dados',
    'Epidemiologia-saúde coletiva',
    'Farmácia',
    'Fisioterapia',
    'Gastroenterologia',
    'Geriatria',
    'Ginecologia',
    'Hepatologia',
    'Infectologia',
    'Mastologia',
    'Medicina',
    'Medicina intensiva',
    'Medicina Tropical',
    'Microbiologia',
    'Nefrologia',
    'Neurologia',
    'Nutrição',
    'Obstetrícia',
    'Odontologia',
    'Oftalmologia',
    'Onco-hematologia',
    'Oncologia clínica',
    'Otorrinolaringologia',
    'Patologia',
    'Pedagogia',
    'Pediatria',
    'Pneumologia',
    'Processamento de dados',
    'Psicologia',
    'Psiquiatria',
    'Radiologia',
    'Radioterapia',
    'Reumatologia',
    'Saúde coletiva',
    'Serviço social',
    'Terapia ocupacional',
    'Transplante',
    'Urologia',
    'outros',
]

INSTITUICOES_PROPONENTE_INICIAIS = [
    'HUB/EBSERH',
    'UNB/Faculdade de Agronomia e Medicina Veterinária',
    'UNB/Faculdade de Arquitetura e Urbanismo',
    'UNB/Faculdade de Ciência da Informação',
    'UNB/Faculdade de Ciências da Saúde',
    'UNB/Faculdade de Comunicação',
    'UNB/Faculdade de Direito',
    'UNB/Faculdade de Economia, Administração, Contabilidade e Gestão de Políticas Públicas',
    'UNB/Faculdade de Educação',
    'UNB/Faculdade de Educação Física',
    'UNB/Faculdade de Medicina',
    'UNB/Faculdade de Tecnologia',
    'UNB/Faculdade UnB Ceilândia',
    'UNB/Faculdade UnB Gama',
    'UNB/Faculdade UnB Planaltina',
    'UNB/Instituto de Artes',
    'UNB/Instituto de Ciência Política',
    'UNB/Instituto de Ciências Biológicas',
    'UNB/Instituto de Ciências Exatas',
    'UNB/Instituto de Ciências Humanas',
    'UNB/Instituto de Ciências Sociais',
    'UNB/Instituto de Física',
    'UNB/Instituto de Geociências',
    'UNB/Instituto de Letras',
    'UNB/Instituto de Psicologia',
    'UNB/Instituto de Química',
    'UNB/Instituto de Relações Internacionais',
]

CLASSIFICACOES_INSTITUCIONAIS_FIXAS = [
    'Pesquisa com seres humanos SEM intervenção',
    'Pesquisa com seres humanos COM intervenção',
    'Pesquisa QUE NÃO ENVOLVE seres humanos',
]

FUNCOES_PARTICIPACAO_INICIAIS = [
    'Pesquisador principal',
    'Sub-investigador',
    'Coordenador',
    'Equipe de pesquisa',
]

VINCULOS_PARTICIPACAO_INICIAIS = [
    'Não informado',
]

UNIDADES_ORGANIZACIONAIS_INICIAIS = [
    'GERÊNCIA DE ATENÇÃO À SAÚDE',
    'Unidade Multiprofissional',
    'Unidade do Sistema Urinário',
    'Unidade do Sistema Cardiovascular',
    'Unidade de Vigilância em Saúde',
    'Unidade de Urgência e Emergência',
    'Unidade de Transplantes',
    'Unidade de Terapia Intensiva Neonatal',
    'Unidade de Terapia Intensiva Adulto',
    'Unidade de Sistemas de Informação e Inteligência de Dados',
    'Unidade de Serviços Gerais',
    'Unidade de Saúde Ocupacional e Segurança do Trabalho',
    'Unidade de Saúde Mental',
    'Unidade de Saúde da Mulher',
    'Unidade de Saúde Bucal',
    'Unidade de Regulação Assistencial',
    'Unidade de Planejamento, Gestão de Riscos e Controles Internos',
    'Unidade de Planejamento e Gestão Orçamentária',
    'Unidade de Planejamento e Dimensionamento de Estoques',
    'Unidade de Patrimônio',
    'Unidade de Oncologia',
    'Unidade de Laboratório de Análises Clínicas',
    'Unidade de Infraestrutura, Suporte e Segurança de Tecnologia da Informação',
    'Unidade de Hematologia e Hemoterapia',
    'Unidade de Gestão e Processamento da Informação Assistencial',
    'Unidade de Gestão de Pós-Graduação',
    'Unidade de Gestão de Graduação, Ensino Técnico e Extensão',
    'Unidade de Gestão da Qualidade e Segurança do Paciente',
    'Unidade de Gestão da Pesquisa',
    'Unidade de Gestão da Inovação Tecnológica em Saúde',
    'Unidade de Fiscalização Administrativa de Contratos',
    'Unidade de Execução Orçamentária e Financeira',
    'Unidade de Especialidades Clínicas',
    'Unidade de e-Saúde',
    'Unidade de Diagnósticos Especializados',
    'Unidade de Diagnóstico por Imagem',
    'Unidade de Desenvolvimento de Pessoal',
    'Unidade de Contratualização',
    'Unidade de Contratos',
    'Unidade de Comunicação Social',
    'Unidade de Compras e Licitações',
    'Unidade de Clínica Cirúrgica',
    'Unidade de Bloco Cirúrgico e Processamento de Materiais Esterilizados',
    'Unidade de Anatomia Patológica',
    'Unidade de Ambulatório',
    'Unidade de Almoxarifado e Controle de Estoques',
    'Unidade de Administração de Pessoal',
    'Unidade da Criança e do Adolescente',
    'SUPERINTENDÊNCIA',
    'Setor de Tecnologia da Informação e Saúde Digital',
    'Setor de Paciente Crítico',
    'Setor de Infraestrutura Física',
    'Setor de Hotelaria Hospitalar',
    'Setor de Governança e Estratégia',
    'Setor de Gestão Orçamentária e Financeira',
    'Setor de Gestão do Ensino',
    'Setor de Gestão da Qualidade',
    'Setor de Gestão da Pesquisa e da Inovação Tecnológica em Saúde',
    'Setor de Farmácia Hospitalar',
    'Setor de Engenharia Clínica',
    'Setor de Contratualização e Regulação',
    'Setor de Contabilidade',
    'Setor de Apoio Diagnóstico e Terapêutico',
    'Setor de Administração',
    'Setor de Abastecimento Farmacêutico e Suprimentos',
    'GERÊNCIA DE ENSINO E PESQUISA',
    'GERÊNCIA ADMINISTRATIVA',
    'Divisão Médica',
    'Divisão de Logística e Infraestrutura',
    'Divisão de Gestão do Cuidado',
    'Divisão de Gestão de Pessoas',
    'Divisão de Enfermagem',
    'Divisão de Apoio Diagnóstico e Terapêutico',
    'Divisão de Administração e Finanças',
    'OUTRO',
]


def _garantir_tipos_pesquisa_iniciais():
    for nome in TIPOS_PESQUISA_INICIAIS:
        TipoPesquisa.objects.get_or_create(nome_tipo=nome)
    TipoPesquisa.objects.exclude(nome_tipo__in=TIPOS_PESQUISA_INICIAIS).delete()


def _garantir_linhas_pesquisa_iniciais():
    for nome in LINHAS_PESQUISA_INICIAIS:
        LinhaPesquisa.objects.get_or_create(nome_linha=nome)


def _garantir_classificacoes_fixas():
    for nome in CLASSIFICACOES_INSTITUCIONAIS_FIXAS:
        ClassificacaoInstitucional.objects.get_or_create(nome_classificacao=nome)


def _garantir_especialidades_iniciais():
    for nome in ESPECIALIDADES_PROPONENTE_INICIAIS:
        EspecialidadeProponente.objects.get_or_create(nome_especialidade=nome)
    EspecialidadeProponente.objects.exclude(nome_especialidade__in=ESPECIALIDADES_PROPONENTE_INICIAIS).delete()


def _garantir_instituicoes_iniciais():
    for nome in INSTITUICOES_PROPONENTE_INICIAIS:
        InstituicaoProponente.objects.get_or_create(nome_instituicao=nome)
    InstituicaoProponente.objects.exclude(nome_instituicao__in=INSTITUICOES_PROPONENTE_INICIAIS).delete()


def _garantir_unidades_iniciais():
    for nome in UNIDADES_ORGANIZACIONAIS_INICIAIS:
        Unidade.objects.get_or_create(nome_unidade=nome)
    Unidade.objects.exclude(nome_unidade__in=UNIDADES_ORGANIZACIONAIS_INICIAIS).delete()


def _garantir_funcoes_participacao_iniciais():
    for nome in FUNCOES_PARTICIPACAO_INICIAIS:
        FuncaoPesquisador.objects.get_or_create(nome_funcao=nome)
    FuncaoPesquisador.objects.exclude(nome_funcao__in=FUNCOES_PARTICIPACAO_INICIAIS).delete()


def _garantir_vinculos_participacao_iniciais():
    for nome in VINCULOS_PARTICIPACAO_INICIAIS:
        VinculoPesquisador.objects.get_or_create(nome_vinculo=nome)


def _formatar_trimestre(data):
    if not data:
        return '-'

    trimestre = ((data.month - 1) // 3) + 1
    return f'{trimestre}o trimestre ({data.year})'


def _formatar_duracao_em_dias(data_inicio, data_fim):
    if not data_inicio or not data_fim:
        return '-'

    dias = (data_fim - data_inicio).days
    if dias < 0:
        return f'{abs(dias)} dias (ordem de datas invertida)'
    return f'{dias} dias'

class UnidadeForm(forms.ModelForm):
    """Formulário para criar nova unidade"""
    class Meta:
        model = Unidade
        fields = ['nome_unidade']
        widgets = {
            'nome_unidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Departamento de Pesquisa'
            })
        }
        labels = {
            'nome_unidade': 'Nome da Unidade'
        }


class ProjetoForm(forms.ModelForm):
    tipo_pesq = forms.ModelChoiceField(
        queryset=TipoPesquisa.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_tipo_pesq_select'
        }),
        label='Tipo de Pesquisa',
        empty_label='-- Selecionar tipo --'
    )

    classificacao = forms.ModelChoiceField(
        queryset=ClassificacaoInstitucional.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_classificacao_select'
        }),
        label='Classificação Institucional',
        empty_label='-- Selecionar classificação --'
    )

    especialidade_proponente = forms.ModelChoiceField(
        queryset=EspecialidadeProponente.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_especialidade_select'
        }),
        label='Especialidade do Proponente',
        empty_label='-- Selecionar especialidade --'
    )

    instituicao_proponente = forms.ModelChoiceField(
        queryset=InstituicaoProponente.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_instituicao_select'
        }),
        label='Instituição Proponente',
        empty_label='-- Selecionar instituição --'
    )

    linhas_pesq = forms.ModelChoiceField(
        queryset=LinhaPesquisa.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_linha_pesquisa_select'
        }),
        label='Linhas de Pesquisa',
        empty_label='-- Selecionar linha --'
    )

    linhas_pesq = forms.ModelChoiceField(
        queryset=LinhaPesquisa.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_linha_pesquisa_select'
        }),
        label='Linhas de Pesquisa',
        empty_label='-- Selecionar linha --'
    )
    
    class Meta:
        model = Projeto
        fields = [
            'sig_id_projeto', 'sig_id_pesq', 'titulo', 'data_ent_sig', 'data_lib_analise', 
            'tipo_pesq', 'desenvolvimento_tecnologico', 'multicentrico',
            'especialidade_proponente', 'instituicao_proponente', 'tipo_fomento', 'formalizacao_instrumento', 'linhas_pesq', 'inicio_coleta',
            'fim_coleta', 'data_aprovacao_inst', 'parecer_cep',
            'data_parecer_cep', 'papel_HUB_multi', 'parceria_HUB_UNB',
            'HUB_proponente'
        ]
        widgets = {
            'sig_id_projeto': forms.TextInput(attrs={'class': 'form-control'}),
            'sig_id_pesq': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'data_ent_sig': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_lib_analise': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_pesq': forms.Select(attrs={'class': 'form-control'}),
            'desenvolvimento_tecnologico': forms.Select(attrs={'class': 'form-control'}),
            'multicentrico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'especialidade_proponente': forms.Select(attrs={'class': 'form-control'}),
            'instituicao_proponente': forms.Select(attrs={'class': 'form-control'}),
            'tipo_fomento': forms.Select(attrs={'class': 'form-control'}),
            'formalizacao_instrumento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'linhas_pesq': forms.Select(attrs={'class': 'form-control'}),
            'inicio_coleta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fim_coleta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_aprovacao_inst': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'parecer_cep': forms.Select(attrs={'class': 'form-control'}),
            'data_parecer_cep': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'papel_HUB_multi': forms.Select(attrs={'class': 'form-control'}),
            'parceria_HUB_UNB': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'HUB_proponente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'sig_id_projeto': 'SIG ID do Projeto *',
            'sig_id_pesq': 'SIG ID da Pesquisa',
            'titulo': 'Título do Projeto',
            'data_ent_sig': 'Data de Entrada no SIG',
            'data_lib_analise': 'Data de Liberação para Análise',
            'tipo_pesq': 'Tipo de Pesquisa',
            'desenvolvimento_tecnologico': 'Desenvolvimento Tecnológico',
            'multicentrico': 'Multicêntrico',
            'especialidade_proponente': 'Especialidade do Proponente',
            'instituicao_proponente': 'Instituição Proponente',
            'tipo_fomento': 'Tipo de Fomento',
            'formalizacao_instrumento': 'Formalização de Fomento',
            'linhas_pesq': 'Linhas de Pesquisa',
            'inicio_coleta': 'Início da Coleta',
            'fim_coleta': 'Fim da Coleta',
            'data_aprovacao_inst': 'Data de Aprovação Institucional',
            'parecer_cep': 'Parecer CEP',
            'data_parecer_cep': 'Data do Parecer CEP',
            'papel_HUB_multi': 'Papel do HUB',
            'parceria_HUB_UNB': 'Parceria HUB/UNB',
            'HUB_proponente': 'HUB Proponente',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _garantir_tipos_pesquisa_iniciais()
        _garantir_linhas_pesquisa_iniciais()
        _garantir_classificacoes_fixas()
        _garantir_especialidades_iniciais()
        _garantir_instituicoes_iniciais()
        self.fields['tipo_pesq'].queryset = TipoPesquisa.objects.all().order_by('nome_tipo')
        self.fields['linhas_pesq'].queryset = LinhaPesquisa.objects.all().order_by('nome_linha')
        self.fields['classificacao'].queryset = ClassificacaoInstitucional.objects.all().order_by('nome_classificacao')
        self.fields['especialidade_proponente'].queryset = EspecialidadeProponente.objects.all().order_by('nome_especialidade')
        self.fields['instituicao_proponente'].queryset = InstituicaoProponente.objects.all().order_by('nome_instituicao')

        tipo_pesq_atual = getattr(self.instance, 'tipo_pesq', None)
        if tipo_pesq_atual:
            tipo_obj = TipoPesquisa.objects.filter(nome_tipo=tipo_pesq_atual).first()
            if tipo_obj:
                self.initial['tipo_pesq'] = tipo_obj

        linha_atual = getattr(self.instance, 'linhas_pesq', None)
        if linha_atual:
            linha_obj, _ = LinhaPesquisa.objects.get_or_create(nome_linha=linha_atual)
            self.initial['linhas_pesq'] = linha_obj

        if self.instance and self.instance.pk:
            classificacao_atual = self.instance.classificacoes.first()
            if classificacao_atual:
                self.initial['classificacao'] = classificacao_atual

        especialidade_atual = getattr(self.instance, 'especialidade_proponente', None)
        if especialidade_atual:
            especialidade_obj = EspecialidadeProponente.objects.filter(nome_especialidade=especialidade_atual).first()
            if especialidade_obj:
                self.initial['especialidade_proponente'] = especialidade_obj

        instituicao_atual = getattr(self.instance, 'instituicao_proponente', None)
        if instituicao_atual:
            instituicao_obj = InstituicaoProponente.objects.filter(nome_instituicao=instituicao_atual).first()
            if instituicao_obj:
                self.initial['instituicao_proponente'] = instituicao_obj

    def clean(self):
        cleaned_data = super().clean()

        data_ent_sig = cleaned_data.get('data_ent_sig')
        data_lib_analise = cleaned_data.get('data_lib_analise')
        data_aprovacao_inst = cleaned_data.get('data_aprovacao_inst')
        inicio_coleta = cleaned_data.get('inicio_coleta')

        if data_ent_sig:
            if data_lib_analise and data_lib_analise <= data_ent_sig:
                self.add_error(
                    'data_lib_analise',
                    'A Data de Liberação para Análise deve ser posterior à Data de Entrada no SIG.',
                )

            if data_aprovacao_inst and data_aprovacao_inst <= data_ent_sig:
                self.add_error(
                    'data_aprovacao_inst',
                    'A Data de Aprovação Institucional deve ser posterior à Data de Entrada no SIG.',
                )

            if inicio_coleta and inicio_coleta <= data_ent_sig:
                self.add_error(
                    'inicio_coleta',
                    'A data de Início da Coleta deve ser posterior à Data de Entrada no SIG.',
                )

        tipo_fomento = cleaned_data.get('tipo_fomento')
        formalizacao_instrumento = cleaned_data.get('formalizacao_instrumento')

        if tipo_fomento and not formalizacao_instrumento:
            self.add_error(
                'formalizacao_instrumento',
                'Marque este campo quando houver fonte de fomento informada.',
            )

        if not tipo_fomento:
            cleaned_data['formalizacao_instrumento'] = False

        return cleaned_data

    def save(self, commit=True):
        projeto = super().save(commit=False)

        tipo_pesq = self.cleaned_data.get('tipo_pesq')
        projeto.tipo_pesq = tipo_pesq.nome_tipo if tipo_pesq else None

        linha_pesquisa = self.cleaned_data.get('linhas_pesq')
        projeto.linhas_pesq = linha_pesquisa.nome_linha if linha_pesquisa else None

        linha_pesquisa = self.cleaned_data.get('linhas_pesq')
        projeto.linhas_pesq = linha_pesquisa.nome_linha if linha_pesquisa else None

        especialidade = self.cleaned_data.get('especialidade_proponente')
        projeto.especialidade_proponente = especialidade.nome_especialidade if especialidade else None

        instituicao = self.cleaned_data.get('instituicao_proponente')
        projeto.instituicao_proponente = instituicao.nome_instituicao if instituicao else None
        projeto.formalizacao_instrumento = bool(self.cleaned_data.get('formalizacao_instrumento'))

        if commit:
            projeto.save()
        
        # Processar classificação
        classificacao = self.cleaned_data.get('classificacao')
        projeto.classificacoes.clear()
        if classificacao:
            projeto.classificacoes.add(classificacao)
        
        return projeto


class ProjetoEditForm(forms.ModelForm):
    """Formulário de edição de projeto - não permite alterar sig_id_projeto (chave primária)"""
    tipo_pesq = forms.ModelChoiceField(
        queryset=TipoPesquisa.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_tipo_pesq_select'
        }),
        label='Tipo de Pesquisa',
        empty_label='-- Selecionar tipo --'
    )

    classificacao = forms.ModelChoiceField(
        queryset=ClassificacaoInstitucional.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_classificacao_select'
        }),
        label='Classificação Institucional',
        empty_label='-- Selecionar classificação --'
    )

    especialidade_proponente = forms.ModelChoiceField(
        queryset=EspecialidadeProponente.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_especialidade_select'
        }),
        label='Especialidade do Proponente',
        empty_label='-- Selecionar especialidade --'
    )

    instituicao_proponente = forms.ModelChoiceField(
        queryset=InstituicaoProponente.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_instituicao_select'
        }),
        label='Instituição Proponente',
        empty_label='-- Selecionar instituição --'
    )
    
    class Meta:
        model = Projeto
        fields = [
            'sig_id_pesq', 'titulo', 'data_ent_sig', 'data_lib_analise',
            'tipo_pesq', 'desenvolvimento_tecnologico', 'multicentrico',
            'especialidade_proponente', 'instituicao_proponente', 'tipo_fomento', 'formalizacao_instrumento', 'linhas_pesq', 'inicio_coleta',
            'fim_coleta', 'data_aprovacao_inst', 'parecer_cep',
            'data_parecer_cep', 'papel_HUB_multi', 'parceria_HUB_UNB',
            'HUB_proponente'
        ]
        widgets = {
            'sig_id_pesq': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'data_ent_sig': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_lib_analise': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_pesq': forms.Select(attrs={'class': 'form-control'}),
            'desenvolvimento_tecnologico': forms.Select(attrs={'class': 'form-control'}),
            'multicentrico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'especialidade_proponente': forms.Select(attrs={'class': 'form-control'}),
            'instituicao_proponente': forms.Select(attrs={'class': 'form-control'}),
            'tipo_fomento': forms.Select(attrs={'class': 'form-control'}),
            'formalizacao_instrumento': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'linhas_pesq': forms.Select(attrs={'class': 'form-control'}),
            'inicio_coleta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fim_coleta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_aprovacao_inst': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'parecer_cep': forms.Select(attrs={'class': 'form-control'}),
            'data_parecer_cep': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'papel_HUB_multi': forms.Select(attrs={'class': 'form-control'}),
            'parceria_HUB_UNB': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'HUB_proponente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'sig_id_pesq': 'SIG ID da Pesquisa',
            'titulo': 'Título do Projeto',
            'data_ent_sig': 'Data de Entrada no SIG',
            'data_lib_analise': 'Data de Liberação para Análise',
            'tipo_pesq': 'Tipo de Pesquisa',
            'desenvolvimento_tecnologico': 'Desenvolvimento Tecnológico',
            'multicentrico': 'Multicêntrico',
            'especialidade_proponente': 'Especialidade do Proponente',
            'instituicao_proponente': 'Instituição Proponente',
            'tipo_fomento': 'Tipo de Fomento',
            'formalizacao_instrumento': 'Formalização de Fomento',
            'linhas_pesq': 'Linhas de Pesquisa',
            'inicio_coleta': 'Início da Coleta',
            'fim_coleta': 'Fim da Coleta',
            'data_aprovacao_inst': 'Data de Aprovação Institucional',
            'parecer_cep': 'Parecer CEP',
            'data_parecer_cep': 'Data do Parecer CEP',
            'papel_HUB_multi': 'Papel do HUB',
            'parceria_HUB_UNB': 'Parceria HUB/UNB',
            'HUB_proponente': 'HUB Proponente',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _garantir_tipos_pesquisa_iniciais()
        _garantir_linhas_pesquisa_iniciais()
        _garantir_classificacoes_fixas()
        _garantir_especialidades_iniciais()
        _garantir_instituicoes_iniciais()
        self.fields['tipo_pesq'].queryset = TipoPesquisa.objects.all().order_by('nome_tipo')
        self.fields['linhas_pesq'].queryset = LinhaPesquisa.objects.all().order_by('nome_linha')
        self.fields['classificacao'].queryset = ClassificacaoInstitucional.objects.all().order_by('nome_classificacao')
        self.fields['especialidade_proponente'].queryset = EspecialidadeProponente.objects.all().order_by('nome_especialidade')
        self.fields['instituicao_proponente'].queryset = InstituicaoProponente.objects.all().order_by('nome_instituicao')

        tipo_pesq_atual = getattr(self.instance, 'tipo_pesq', None)
        if tipo_pesq_atual:
            tipo_obj = TipoPesquisa.objects.filter(nome_tipo=tipo_pesq_atual).first()
            if tipo_obj:
                self.initial['tipo_pesq'] = tipo_obj

        linha_atual = getattr(self.instance, 'linhas_pesq', None)
        if linha_atual:
            linha_obj, _ = LinhaPesquisa.objects.get_or_create(nome_linha=linha_atual)
            self.initial['linhas_pesq'] = linha_obj

        if self.instance and self.instance.pk:
            classificacao_atual = self.instance.classificacoes.first()
            if classificacao_atual:
                self.initial['classificacao'] = classificacao_atual

        especialidade_atual = getattr(self.instance, 'especialidade_proponente', None)
        if especialidade_atual:
            especialidade_obj = EspecialidadeProponente.objects.filter(nome_especialidade=especialidade_atual).first()
            if especialidade_obj:
                self.initial['especialidade_proponente'] = especialidade_obj

        instituicao_atual = getattr(self.instance, 'instituicao_proponente', None)
        if instituicao_atual:
            instituicao_obj = InstituicaoProponente.objects.filter(nome_instituicao=instituicao_atual).first()
            if instituicao_obj:
                self.initial['instituicao_proponente'] = instituicao_obj

    def clean(self):
        cleaned_data = super().clean()

        data_ent_sig = cleaned_data.get('data_ent_sig')
        data_lib_analise = cleaned_data.get('data_lib_analise')
        data_aprovacao_inst = cleaned_data.get('data_aprovacao_inst')
        inicio_coleta = cleaned_data.get('inicio_coleta')

        if data_ent_sig:
            if data_lib_analise and data_lib_analise <= data_ent_sig:
                self.add_error(
                    'data_lib_analise',
                    'A Data de Liberação para Análise deve ser posterior à Data de Entrada no SIG.',
                )

            if data_aprovacao_inst and data_aprovacao_inst <= data_ent_sig:
                self.add_error(
                    'data_aprovacao_inst',
                    'A Data de Aprovação Institucional deve ser posterior à Data de Entrada no SIG.',
                )

            if inicio_coleta and inicio_coleta <= data_ent_sig:
                self.add_error(
                    'inicio_coleta',
                    'A data de Início da Coleta deve ser posterior à Data de Entrada no SIG.',
                )

        tipo_fomento = cleaned_data.get('tipo_fomento')
        formalizacao_instrumento = cleaned_data.get('formalizacao_instrumento')

        if tipo_fomento and not formalizacao_instrumento:
            self.add_error(
                'formalizacao_instrumento',
                'Marque este campo quando houver fonte de fomento informada.',
            )

        if not tipo_fomento:
            cleaned_data['formalizacao_instrumento'] = False

        return cleaned_data

    def save(self, commit=True):
        projeto = super().save(commit=False)

        tipo_pesq = self.cleaned_data.get('tipo_pesq')
        projeto.tipo_pesq = tipo_pesq.nome_tipo if tipo_pesq else None

        especialidade = self.cleaned_data.get('especialidade_proponente')
        projeto.especialidade_proponente = especialidade.nome_especialidade if especialidade else None

        instituicao = self.cleaned_data.get('instituicao_proponente')
        projeto.instituicao_proponente = instituicao.nome_instituicao if instituicao else None
        projeto.formalizacao_instrumento = bool(self.cleaned_data.get('formalizacao_instrumento'))

        if commit:
            projeto.save()
        
        # Processar classificação
        classificacao = self.cleaned_data.get('classificacao')
        projeto.classificacoes.clear()
        if classificacao:
            projeto.classificacoes.add(classificacao)
        
        return projeto


class ParticipacaoForm(forms.ModelForm):
    vinculo = forms.ModelChoiceField(
        queryset=VinculoPesquisador.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_vinculo_select'}),
        label='Vínculo com o projeto',
        empty_label='-- Selecionar vínculo --',
    )
    funcao = forms.ModelChoiceField(
        queryset=FuncaoPesquisador.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_funcao_select'}),
        label='Função no projeto',
        empty_label='-- Selecionar função --',
    )

    class Meta:
        model = Participacao
        fields = ['pesquisador', 'vinculo', 'funcao']
        widgets = {
            'pesquisador': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'pesquisador': 'Pesquisador',
        }
    
    def __init__(self, *args, projeto=None, **kwargs):
        super().__init__(*args, **kwargs)
        _garantir_funcoes_participacao_iniciais()
        _garantir_vinculos_participacao_iniciais()

        self.fields['vinculo'].queryset = VinculoPesquisador.objects.all().order_by('nome_vinculo')
        self.fields['funcao'].queryset = FuncaoPesquisador.objects.all().order_by('nome_funcao')
        if projeto:
            # Excluir pesquisadores que já participam do projeto
            participantes_ids = Participacao.objects.filter(projeto=projeto).values_list('pesquisador_id', flat=True)
            pesquisador_field = self.fields.get('pesquisador')
            if isinstance(pesquisador_field, forms.ModelChoiceField):
                pesquisador_field.queryset = Pesquisador.objects.exclude(pk__in=participantes_ids)


class EnvolveForm(forms.Form):
    unidade = forms.ModelChoiceField(
        queryset=Unidade.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_unidade_select'}),
        label='Unidade Organizacional',
        empty_label='-- Selecionar unidade --',
    )

    def __init__(self, *args, projeto=None, **kwargs):
        super().__init__(*args, **kwargs)
        _garantir_unidades_iniciais()

        queryset = Unidade.objects.all().order_by('nome_unidade')
        if projeto:
            unidades_ids = Envolve.objects.filter(projeto=projeto).values_list('unidade_id', flat=True)
            queryset = queryset.exclude(pk__in=unidades_ids)

        self.fields['unidade'].queryset = queryset


class ParceriaHospitalForm(forms.Form):
    hospital = forms.ModelChoiceField(
        queryset=HospitalHubBrasil.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_hospital_select'}),
        label='Hospital da Rede HUBrasil',
        empty_label='-- Selecionar hospital --',
    )

    def __init__(self, *args, projeto=None, **kwargs):
        super().__init__(*args, **kwargs)

        queryset = HospitalHubBrasil.objects.all().order_by('nome_hospital')
        if projeto:
            hospitais_ids = ParceriaHospital.objects.filter(projeto=projeto).values_list('hospital_id', flat=True)
            queryset = queryset.exclude(pk__in=hospitais_ids)

        self.fields['hospital'].queryset = queryset


class ConfiguracaoAvisoForm(forms.ModelForm):
    """Formulário da mensagem/configuração global dos avisos periódicos."""
    class Meta:
        model = ConfiguracaoAviso
        fields = ['assunto', 'mensagem', 'intervalo_dias', 'ativo']
        widgets = {
            'assunto': forms.TextInput(attrs={'class': 'form-control'}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'intervalo_dias': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'assunto': 'Assunto (usado no e-mail)',
            'mensagem': 'Mensagem do aviso',
            'intervalo_dias': 'Intervalo entre avisos (dias)',
            'ativo': 'Envio de avisos ativo',
        }


@login_required
def criar_unidade_ajax(request):
    """View AJAX para criar nova unidade"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        nome = request.POST.get('nome_unidade', '').strip()
        if nome:
            unidade, created = Unidade.objects.get_or_create(nome_unidade=nome)
            return JsonResponse({
                'success': True,
                'id': unidade.pk,
                'nome': unidade.nome_unidade,
                'created': created
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Nome da unidade não pode estar vazio'
            }, status=400)
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def criar_hospital_ajax(request):
    """View AJAX para criar novo hospital parceiro"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        nome = request.POST.get('nome_hospital', '').strip()
        if nome:
            hospital, created = HospitalHubBrasil.objects.get_or_create(nome_hospital=nome)
            return JsonResponse({
                'success': True,
                'id': hospital.pk,
                'nome': hospital.nome_hospital,
                'created': created
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Nome do hospital não pode estar vazio'
            }, status=400)
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def criar_classificacao_ajax(request):
    """View AJAX para criar nova classificação institucional"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        nome = request.POST.get('nome_classificacao', '').strip()
        if nome:
            classificacao, created = ClassificacaoInstitucional.objects.get_or_create(nome_classificacao=nome)
            return JsonResponse({
                'success': True,
                'id': classificacao.pk,
                'nome': classificacao.nome_classificacao,
                'created': created
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Nome da classificação não pode estar vazio'
            }, status=400)
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def criar_tipo_pesquisa_ajax(request):
    """View AJAX para criar novo tipo de pesquisa"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        nome = request.POST.get('nome_tipo', '').strip()
        if nome:
            tipo, created = TipoPesquisa.objects.get_or_create(nome_tipo=nome)
            return JsonResponse({
                'success': True,
                'id': tipo.pk,
                'nome': tipo.nome_tipo,
                'created': created
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Nome do tipo de pesquisa não pode estar vazio'
            }, status=400)
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def criar_linha_pesquisa_ajax(request):
    """View AJAX para criar nova linha de pesquisa"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        nome = request.POST.get('nome_linha', '').strip()
        if nome:
            linha, created = LinhaPesquisa.objects.get_or_create(nome_linha=nome)
            return JsonResponse({
                'success': True,
                'id': linha.pk,
                'nome': linha.nome_linha,
                'created': created
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Nome da linha de pesquisa não pode estar vazio'
            }, status=400)
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def criar_especialidade_ajax(request):
    """View AJAX para criar nova especialidade do proponente"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        nome = request.POST.get('nome_especialidade', '').strip()
        if nome:
            especialidade, created = EspecialidadeProponente.objects.get_or_create(nome_especialidade=nome)
            return JsonResponse({
                'success': True,
                'id': especialidade.pk,
                'nome': especialidade.nome_especialidade,
                'created': created
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Nome da especialidade não pode estar vazio'
            }, status=400)
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def criar_instituicao_ajax(request):
    """View AJAX para criar nova instituição proponente"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        nome = request.POST.get('nome_instituicao', '').strip()
        if nome:
            instituicao, created = InstituicaoProponente.objects.get_or_create(nome_instituicao=nome)
            return JsonResponse({
                'success': True,
                'id': instituicao.pk,
                'nome': instituicao.nome_instituicao,
                'created': created
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Nome da instituição não pode estar vazio'
            }, status=400)
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def criar_vinculo_ajax(request):
    """View AJAX para criar novo vínculo do pesquisador"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        nome = request.POST.get('nome_vinculo', '').strip()
        if nome:
            vinculo, created = VinculoPesquisador.objects.get_or_create(nome_vinculo=nome)
            return JsonResponse({
                'success': True,
                'id': vinculo.pk,
                'nome': vinculo.nome_vinculo,
                'created': created
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Nome do vínculo não pode estar vazio'
            }, status=400)
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def criar_funcao_ajax(request):
    """View AJAX para criar nova função do pesquisador"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        nome = request.POST.get('nome_funcao', '').strip()
        if nome:
            funcao, created = FuncaoPesquisador.objects.get_or_create(nome_funcao=nome)
            return JsonResponse({
                'success': True,
                'id': funcao.pk,
                'nome': funcao.nome_funcao,
                'created': created
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Nome da função não pode estar vazio'
            }, status=400)
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def lista_projetos(request):
    # Se o usuário for admin/staff, mostra todos os projetos
    if request.user.is_staff or request.user.is_superuser:
        projetos = Projeto.objects.prefetch_related('participacao_set__pesquisador__user').all()
    else:
        # Filtrar apenas projetos em que o usuário logado participa
        try:
            pesquisador = Pesquisador.objects.get(user=request.user)
            projetos = Projeto.objects.filter(
                participacao__pesquisador=pesquisador
            ).prefetch_related('participacao_set__pesquisador__user').distinct()
        except Pesquisador.DoesNotExist:
            # Se o usuário não é um pesquisador, não mostra nenhum projeto
            projetos = Projeto.objects.none()

    projetos = list(projetos)
    for projeto in projetos:
        setattr(projeto, 'trimestre_aprovacao_inst', _formatar_trimestre(projeto.data_aprovacao_inst))
        setattr(projeto, 'tempo_aprovacao_entrada_sig', _formatar_duracao_em_dias(
            projeto.data_ent_sig,
            projeto.data_aprovacao_inst,
        ))
        setattr(projeto, 'tempo_aprovacao_liberacao_analise', _formatar_duracao_em_dias(
            projeto.data_lib_analise,
            projeto.data_aprovacao_inst,
        ))
    
    return render(request, 'projetos/lista_projetos.html', {'projetos': projetos})

@login_required
def cadastro_projeto(request):
    if request.method == 'POST':
        form = ProjetoForm(request.POST)
        if form.is_valid():
            projeto = form.save()
            
            # Adicionar o usuário atual como líder do projeto
            try:
                pesquisador = Pesquisador.objects.get(user=request.user)
                _garantir_funcoes_participacao_iniciais()
                funcao_lider, _ = FuncaoPesquisador.objects.get_or_create(nome_funcao='Líder')
                Participacao.objects.create(
                    pesquisador=pesquisador,
                    projeto=projeto,
                    funcao=funcao_lider
                )
            except Pesquisador.DoesNotExist:
                messages.warning(request, 'Projeto criado, mas você não possui um perfil de pesquisador.')
            
            messages.success(request, 'Projeto cadastrado com sucesso!')
            return redirect('lista_projetos')
    else:
        form = ProjetoForm()
    
    return render(request, 'projetos/cadastro_projeto.html', {'form': form})

@login_required
def editar_projeto(request, projeto_id):
    # Verificar se o usuário é admin
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Você não tem permissão para editar projetos.')
        return redirect('lista_projetos')
    
    projeto = get_object_or_404(Projeto, sig_id_projeto=projeto_id)
    
    if request.method == 'POST':
        form = ProjetoEditForm(request.POST, instance=projeto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Projeto atualizado com sucesso!')
            return redirect('editar_projeto', projeto_id=projeto.sig_id_projeto)
    else:
        form = ProjetoEditForm(instance=projeto)
    
    # Formulários para adicionar vínculos
    participacao_form = ParticipacaoForm(projeto=projeto)
    envolve_form = EnvolveForm(projeto=projeto)
    hospital_form = ParceriaHospitalForm(projeto=projeto)
    
    # Lista de participantes atuais
    participacoes = Participacao.objects.filter(projeto=projeto).select_related('pesquisador__user')
    envolvimentos = Envolve.objects.filter(projeto=projeto).select_related('unidade')
    parcerias_hospitalares = ParceriaHospital.objects.filter(projeto=projeto).select_related('hospital')

    # Avisos periódicos
    config_aviso = ConfiguracaoAviso.carregar()
    aviso_form = ConfiguracaoAvisoForm(instance=config_aviso)
    avisos_enviados = AvisoEnviado.objects.filter(projeto=projeto).select_related('pesquisador__user')
    lider = obter_lider(projeto)

    context = {
        'form': form,
        'projeto': projeto,
        'participacao_form': participacao_form,
        'envolve_form': envolve_form,
        'hospital_form': hospital_form,
        'participacoes': participacoes,
        'envolvimentos': envolvimentos,
        'parcerias_hospitalares': parcerias_hospitalares,
        'aviso_form': aviso_form,
        'avisos_enviados': avisos_enviados,
        'lider_aviso': lider,
    }

    return render(request, 'projetos/editar_projeto.html', context)


@login_required
def salvar_config_aviso(request, projeto_id):
    # Verificar se o usuário é admin
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Você não tem permissão para editar avisos.')
        return redirect('lista_projetos')

    projeto = get_object_or_404(Projeto, sig_id_projeto=projeto_id)
    config = ConfiguracaoAviso.carregar()

    if request.method == 'POST':
        form = ConfiguracaoAvisoForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mensagem de aviso atualizada com sucesso!')
        else:
            messages.error(request, 'Erro ao salvar a configuração de avisos. Verifique os dados.')

    url = reverse('editar_projeto', args=[projeto.sig_id_projeto])
    return redirect(f'{url}#aba-avisos')

@login_required
def adicionar_pesquisador(request, projeto_id):
    # Verificar se o usuário é admin
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Você não tem permissão para adicionar pesquisadores.')
        return redirect('lista_projetos')
    
    projeto = get_object_or_404(Projeto, sig_id_projeto=projeto_id)
    
    if request.method == 'POST':
        form = ParticipacaoForm(request.POST, projeto=projeto)
        if form.is_valid():
            participacao = form.save(commit=False)
            participacao.projeto = projeto
            try:
                participacao.save()
                messages.success(request, f'Pesquisador adicionado com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao adicionar pesquisador: {str(e)}')
        else:
            messages.error(request, 'Erro ao adicionar pesquisador. Verifique os dados.')
    
    return redirect('editar_projeto', projeto_id=projeto.sig_id_projeto)

@login_required
def remover_pesquisador(request, projeto_id, participacao_id):
    # Verificar se o usuário é admin
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Você não tem permissão para remover pesquisadores.')
        return redirect('lista_projetos')
    
    projeto = get_object_or_404(Projeto, sig_id_projeto=projeto_id)
    participacao = get_object_or_404(Participacao, id=participacao_id, projeto=projeto)
    
    pesquisador_nome = participacao.pesquisador.user.get_full_name() or participacao.pesquisador.user.username
    participacao.delete()
    messages.success(request, f'Pesquisador {pesquisador_nome} removido do projeto.')
    
    return redirect('editar_projeto', projeto_id=projeto.sig_id_projeto)


@login_required
def adicionar_unidade(request, projeto_id):
    # Verificar se o usuário é admin
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Você não tem permissão para adicionar unidades.')
        return redirect('lista_projetos')

    projeto = get_object_or_404(Projeto, sig_id_projeto=projeto_id)

    if request.method == 'POST':
        form = EnvolveForm(request.POST, projeto=projeto)
        if form.is_valid():
            unidade = form.cleaned_data['unidade']
            try:
                Envolve.objects.create(projeto=projeto, unidade=unidade)
                messages.success(request, 'Unidade adicionada com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao adicionar unidade: {str(e)}')
        else:
            messages.error(request, 'Erro ao adicionar unidade. Verifique os dados.')

    return redirect('editar_projeto', projeto_id=projeto.sig_id_projeto)


@login_required
def remover_unidade(request, projeto_id, envolve_id):
    # Verificar se o usuário é admin
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Você não tem permissão para remover unidades.')
        return redirect('lista_projetos')

    projeto = get_object_or_404(Projeto, sig_id_projeto=projeto_id)
    envolve = get_object_or_404(Envolve, id=envolve_id, projeto=projeto)

    unidade_nome = envolve.unidade.nome_unidade
    envolve.delete()
    messages.success(request, f'Unidade {unidade_nome} removida do projeto.')

    return redirect('editar_projeto', projeto_id=projeto.sig_id_projeto)


@login_required
def adicionar_hospital(request, projeto_id):
    # Verificar se o usuário é admin
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Você não tem permissão para adicionar hospitais.')
        return redirect('lista_projetos')

    projeto = get_object_or_404(Projeto, sig_id_projeto=projeto_id)

    if request.method == 'POST':
        form = ParceriaHospitalForm(request.POST, projeto=projeto)
        if form.is_valid():
            hospital = form.cleaned_data['hospital']
            try:
                ParceriaHospital.objects.create(projeto=projeto, hospital=hospital)
                messages.success(request, 'Hospital adicionado com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao adicionar hospital: {str(e)}')
        else:
            messages.error(request, 'Erro ao adicionar hospital. Verifique os dados.')

    return redirect('editar_projeto', projeto_id=projeto.sig_id_projeto)


@login_required
def remover_hospital(request, projeto_id, parceria_id):
    # Verificar se o usuário é admin
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Você não tem permissão para remover hospitais.')
        return redirect('lista_projetos')

    projeto = get_object_or_404(Projeto, sig_id_projeto=projeto_id)
    parceria = get_object_or_404(ParceriaHospital, id=parceria_id, projeto=projeto)

    hospital_nome = parceria.hospital.nome_hospital
    parceria.delete()
    messages.success(request, f'Hospital {hospital_nome} removido do projeto.')

    return redirect('editar_projeto', projeto_id=projeto.sig_id_projeto)
