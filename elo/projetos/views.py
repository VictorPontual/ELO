from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Projeto, Participacao
from contas.models import Pesquisador
from django import forms

class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = [
            'titulo', 'data_ent_sig', 'data_lib_analise', 'class_inst', 
            'tipo_pesq', 'desenvolvimento_tecnologico', 'multicentrico',
            'especialidade_proponente', 'linhas_pesq', 'inicio_coleta',
            'fim_coleta', 'data_aprovacao_inst', 'parecer_cep',
            'data_parecer_cep', 'papel_HUB_multi', 'parceria_HUB_UNB',
            'HUB_proponente'
        ]
        widgets = {
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
