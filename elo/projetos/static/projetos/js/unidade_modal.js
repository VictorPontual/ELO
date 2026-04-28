// Modal para criar nova unidade, tipo de pesquisa e especialidade
document.addEventListener('DOMContentLoaded', function() {
    setupDropdownModal('unidade', 'modalCriarUnidade', 'id_unidade_select', 'nomeUnidadeInput', 'botaoCriarUnidade', 'botaoCancelarUnidade');
    setupDropdownModal('hospital', 'modalCriarHospital', 'id_hospital_select', 'nomeHospitalInput', 'botaoCriarHospital', 'botaoCancelarHospital');
    setupDropdownModal('classificacao', 'modalCriarClassificacao', 'id_classificacao_select', 'nomeClassificacaoInput', 'botaoCriarClassificacao', 'botaoCancelarClassificacao');
    setupDropdownModal('tipo_pesquisa', 'modalCriarTipoPesquisa', 'id_tipo_pesq_select', 'nomeTipoPesquisaInput', 'botaoCriarTipoPesquisa', 'botaoCancelarTipoPesquisa');
    setupDropdownModal('especialidade', 'modalCriarEspecialidade', 'id_especialidade_select', 'nomeEspecialidadeInput', 'botaoCriarEspecialidade', 'botaoCancelarEspecialidade');
    setupDropdownModal('instituicao', 'modalCriarInstituicao', 'id_instituicao_select', 'nomeInstituicaoInput', 'botaoCriarInstituicao', 'botaoCancelarInstituicao');
});

function setupDropdownModal(type, modalId, selectId, inputId, buttonId, cancelButtonId) {
    const select = document.getElementById(selectId);
    
    if (!select) return;
    
    // Valor especial para nova opção
    const newOptionValue = `__criar_novo_${type}__`;
    
    // Adicionar opção "Criar Nova"
    const optionCriarNova = document.createElement('option');
    optionCriarNova.value = newOptionValue;
    const labels = {
        unidade: '+ Nova Unidade',
        hospital: '+ Novo Hospital',
        classificacao: '+ Nova Classificacao',
        tipo_pesquisa: '+ Novo Tipo de Pesquisa',
        especialidade: '+ Nova Especialidade',
        instituicao: '+ Nova Instituição'
    };
    optionCriarNova.textContent = labels[type] || '+ Nova Opção';
    optionCriarNova.style.fontWeight = 'bold';
    optionCriarNova.style.color = '#0066cc';
    
    // Inserir como primeira opção após o label padrão
    if (select.options.length > 0 && select.options[0].value === '') {
        select.insertBefore(optionCriarNova, select.options[1]);
    } else {
        select.insertBefore(optionCriarNova, select.options[0]);
    }
    
    // Evento de mudança no select
    select.addEventListener('change', function() {
        if (this.value === newOptionValue) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = 'block';
                document.getElementById(inputId).focus();
            }
            // Resetar select para a primeira opção
            this.value = '';
        }
    });
    
    // Fechar modal
    const botaoFechar = document.querySelector(`#${modalId} .close`);
    if (botaoFechar) {
        botaoFechar.addEventListener('click', function() {
            document.getElementById(modalId).style.display = 'none';
        });
    }
    
    // Fechar clicando fora do modal
    window.addEventListener('click', function(event) {
        const modal = document.getElementById(modalId);
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Cancelar
    const botaoCancelar = document.getElementById(cancelButtonId);
    if (botaoCancelar) {
        botaoCancelar.addEventListener('click', function() {
            document.getElementById(modalId).style.display = 'none';
            document.getElementById(inputId).value = '';
        });
    }
    
    // Criar nova opção
    const botaoCriar = document.getElementById(buttonId);
    if (botaoCriar) {
        botaoCriar.addEventListener('click', function() {
            criarNovaOpcao(type, modalId, selectId, inputId, buttonId);
        });
    }
    
    const input = document.getElementById(inputId);
    if (input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                criarNovaOpcao(type, modalId, selectId, inputId, buttonId);
            }
        });
    }
}

function criarNovaOpcao(type, modalId, selectId, inputId, buttonId) {
    const input = document.getElementById(inputId);
    const nome = input.value.trim();
    
    const nomes = {
        unidade: 'unidade',
        hospital: 'hospital',
        classificacao: 'classificacao',
        tipo_pesquisa: 'tipo de pesquisa',
        especialidade: 'especialidade',
        instituicao: 'instituição'
    };

    if (!nome) {
        alert(`Por favor, digite o nome da ${nomes[type] || 'opção'}`);
        return;
    }
    
    const modal = document.getElementById(modalId);
    const select = document.getElementById(selectId);
    const botao = document.getElementById(buttonId);
    
    // Desabilitar botão durante requisição
    botao.disabled = true;
    botao.textContent = 'Criando...';
    
    // Determinar endpoint e parâmetro baseado no tipo
    let endpoint, paramName, textoBotao;
    if (type === 'unidade') {
        endpoint = window.urlCriarUnidade;
        paramName = 'nome_unidade';
        textoBotao = 'Criar Unidade';
    } else if (type === 'hospital') {
        endpoint = window.urlCriarHospital;
        paramName = 'nome_hospital';
        textoBotao = 'Criar Hospital';
    } else if (type === 'classificacao') {
        endpoint = window.urlCriarClassificacao;
        paramName = 'nome_classificacao';
        textoBotao = 'Criar Classificacao';
    } else if (type === 'tipo_pesquisa') {
        endpoint = window.urlCriarTipoPesquisa;
        paramName = 'nome_tipo';
        textoBotao = 'Criar Tipo de Pesquisa';
    } else if (type === 'instituicao') {
        endpoint = window.urlCriarInstituicao;
        paramName = 'nome_instituicao';
        textoBotao = 'Criar Instituição';
    } else {
        endpoint = window.urlCriarEspecialidade;
        paramName = 'nome_especialidade';
        textoBotao = 'Criar Especialidade';
    }
    
    const params = new URLSearchParams();
    params.append(paramName, nome);
    
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: params
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Adicionar nova opção ao select
            const novaOpcao = document.createElement('option');
            novaOpcao.value = data.id;
            novaOpcao.textContent = data.nome;
            select.appendChild(novaOpcao);
            
            // Selecionar a nova opção
            select.value = data.id;
            
            // Fechar modal
            modal.style.display = 'none';
            input.value = '';
            
            // Feedback ao usuário
            const sucesso = {
                unidade: 'Unidade criada com sucesso!',
                hospital: 'Hospital criado com sucesso!',
                classificacao: 'Classificacao criada com sucesso!',
                tipo_pesquisa: 'Tipo de pesquisa criado com sucesso!',
                especialidade: 'Especialidade criada com sucesso!',
                instituicao: 'Instituição criada com sucesso!'
            };
            alert(sucesso[type] || 'Opção criada com sucesso!');
        } else {
            alert(`Erro ao criar ${nomes[type] || 'opção'}: ` + (data.error || 'Tente novamente'));
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro na comunicação com o servidor');
    })
    .finally(() => {
        botao.disabled = false;
        botao.textContent = textoBotao;
    });
}
