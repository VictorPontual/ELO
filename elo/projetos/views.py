from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Projeto, Participacao
from contas.models import Pesquisador
from django import forms


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

class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = [
            'sig_id_projeto', 'sig_id_pesq', 'titulo', 'data_ent_sig', 'data_lib_analise', 'class_inst', 
            'tipo_pesq', 'desenvolvimento_tecnologico', 'multicentrico',
            'especialidade_proponente', 'linhas_pesq', 'inicio_coleta',
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
            'class_inst': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_pesq': forms.TextInput(attrs={'class': 'form-control'}),
            'desenvolvimento_tecnologico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'multicentrico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'especialidade_proponente': forms.TextInput(attrs={'class': 'form-control'}),
            'linhas_pesq': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'inicio_coleta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fim_coleta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_aprovacao_inst': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'parecer_cep': forms.TextInput(attrs={'class': 'form-control'}),
            'data_parecer_cep': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'papel_HUB_multi': forms.TextInput(attrs={'class': 'form-control'}),
            'parceria_HUB_UNB': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'HUB_proponente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'sig_id_projeto': 'SIG ID do Projeto *',
            'sig_id_pesq': 'SIG ID da Pesquisa',
            'titulo': 'Título do Projeto',
            'data_ent_sig': 'Data de Entrada no SIG',
            'data_lib_analise': 'Data de Liberação para Análise',
            'class_inst': 'Classificação Institucional',
            'tipo_pesq': 'Tipo de Pesquisa',
            'desenvolvimento_tecnologico': 'Desenvolvimento Tecnológico',
            'multicentrico': 'Multicêntrico',
            'especialidade_proponente': 'Especialidade do Proponente',
            'linhas_pesq': 'Linhas de Pesquisa',
            'inicio_coleta': 'Início da Coleta',
            'fim_coleta': 'Fim da Coleta',
            'data_aprovacao_inst': 'Data de Aprovação Institucional',
            'parecer_cep': 'Parecer CEP',
            'data_parecer_cep': 'Data do Parecer CEP',
            'papel_HUB_multi': 'Papel do HUB no Multicêntrico',
            'parceria_HUB_UNB': 'Parceria HUB/UNB',
            'HUB_proponente': 'HUB Proponente',
        }

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

        return cleaned_data


class ProjetoEditForm(forms.ModelForm):
    """Formulário de edição de projeto - não permite alterar sig_id_projeto (chave primária)"""
    class Meta:
        model = Projeto
        fields = [
            'sig_id_pesq', 'titulo', 'data_ent_sig', 'data_lib_analise', 'class_inst', 
            'tipo_pesq', 'desenvolvimento_tecnologico', 'multicentrico',
            'especialidade_proponente', 'linhas_pesq', 'inicio_coleta',
            'fim_coleta', 'data_aprovacao_inst', 'parecer_cep',
            'data_parecer_cep', 'papel_HUB_multi', 'parceria_HUB_UNB',
            'HUB_proponente'
        ]
        widgets = {
            'sig_id_pesq': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'data_ent_sig': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_lib_analise': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'class_inst': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_pesq': forms.TextInput(attrs={'class': 'form-control'}),
            'desenvolvimento_tecnologico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'multicentrico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'especialidade_proponente': forms.TextInput(attrs={'class': 'form-control'}),
            'linhas_pesq': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'inicio_coleta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fim_coleta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_aprovacao_inst': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'parecer_cep': forms.TextInput(attrs={'class': 'form-control'}),
            'data_parecer_cep': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'papel_HUB_multi': forms.TextInput(attrs={'class': 'form-control'}),
            'parceria_HUB_UNB': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'HUB_proponente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'sig_id_pesq': 'SIG ID da Pesquisa',
            'titulo': 'Título do Projeto',
            'data_ent_sig': 'Data de Entrada no SIG',
            'data_lib_analise': 'Data de Liberação para Análise',
            'class_inst': 'Classificação Institucional',
            'tipo_pesq': 'Tipo de Pesquisa',
            'desenvolvimento_tecnologico': 'Desenvolvimento Tecnológico',
            'multicentrico': 'Multicêntrico',
            'especialidade_proponente': 'Especialidade do Proponente',
            'linhas_pesq': 'Linhas de Pesquisa',
            'inicio_coleta': 'Início da Coleta',
            'fim_coleta': 'Fim da Coleta',
            'data_aprovacao_inst': 'Data de Aprovação Institucional',
            'parecer_cep': 'Parecer CEP',
            'data_parecer_cep': 'Data do Parecer CEP',
            'papel_HUB_multi': 'Papel do HUB no Multicêntrico',
            'parceria_HUB_UNB': 'Parceria HUB/UNB',
            'HUB_proponente': 'HUB Proponente',
        }

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

        return cleaned_data


class ParticipacaoForm(forms.ModelForm):
    class Meta:
        model = Participacao
        fields = ['pesquisador', 'atividade']
        widgets = {
            'pesquisador': forms.Select(attrs={'class': 'form-control'}),
            'atividade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Líder, Pesquisador, Colaborador'}),
        }
        labels = {
            'pesquisador': 'Pesquisador',
            'atividade': 'Função/Atividade',
        }
    
    def __init__(self, *args, projeto=None, **kwargs):
        super().__init__(*args, **kwargs)
        if projeto:
            # Excluir pesquisadores que já participam do projeto
            participantes_ids = Participacao.objects.filter(projeto=projeto).values_list('pesquisador_id', flat=True)
            pesquisador_field = self.fields.get('pesquisador')
            if isinstance(pesquisador_field, forms.ModelChoiceField):
                pesquisador_field.queryset = Pesquisador.objects.exclude(pk__in=participantes_ids)


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
                Participacao.objects.create(
                    pesquisador=pesquisador,
                    projeto=projeto,
                    atividade='Líder'
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
    
    # Formulário para adicionar pesquisadores
    participacao_form = ParticipacaoForm(projeto=projeto)
    
    # Lista de participantes atuais
    participacoes = Participacao.objects.filter(projeto=projeto).select_related('pesquisador__user')
    
    context = {
        'form': form,
        'projeto': projeto,
        'participacao_form': participacao_form,
        'participacoes': participacoes,
    }
    
    return render(request, 'projetos/editar_projeto.html', context)

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
