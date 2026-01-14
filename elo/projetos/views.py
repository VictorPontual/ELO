from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Projeto

@login_required
def lista_projetos(request):
    projetos = Projeto.objects.prefetch_related('participacao_set__pesquisador__user').all()
    return render(request, 'projetos/lista_projetos.html', {'projetos': projetos})
