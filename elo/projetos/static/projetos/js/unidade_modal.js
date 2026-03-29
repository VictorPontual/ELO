// Modal para criar nova unidade e classificação
document.addEventListener('DOMContentLoaded', function() {
    setupDropdownModal('unidade', 'modalCriarUnidade', 'id_unidade_select', 'nomeUnidadeInput', 'botaoCriarUnidade', 'botaoCancelarUnidade');
    setupDropdownModal('classificacao', 'modalCriarClassificacao', 'id_classificacao_select', 'nomeClassificacaoInput', 'botaoCriarClassificacao', 'botaoCancelarClassificacao');
});

function setupDropdownModal(type, modalId, selectId, inputId, buttonId, cancelButtonId) {
    const select = document.getElementById(selectId);
    
    if (!select) return;
    
    // Valor especial para nova opção
    const newOptionValue = `__criar_novo_${type}__`;
    
    // Adicionar opção "Criar Nova"
    const optionCriarNova = document.createElement('option');
    optionCriarNova.value = newOptionValue;
    optionCriarNova.textContent = type === 'unidade' ? '+ Nova Unidade' : '+ Nova Classificação';
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
    
    if (!nome) {
        alert(`Por favor, digite o nome da ${type === 'unidade' ? 'unidade' : 'classificação'}`);
        return;
    }
    
    const modal = document.getElementById(modalId);
    const select = document.getElementById(selectId);
    const botao = document.getElementById(buttonId);
    
    // Desabilitar botão durante requisição
    botao.disabled = true;
    botao.textContent = 'Criando...';
    
    // Determinar endpoint e parâmetro baseado no tipo
    let endpoint, paramName;
    if (type === 'unidade') {
        endpoint = window.urlCriarUnidade;
        paramName = 'nome_unidade';
    } else {
        endpoint = window.urlCriarClassificacao;
        paramName = 'nome_classificacao';
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
            alert(`${type === 'unidade' ? 'Unidade' : 'Classificação'} criada com sucesso!`);
        } else {
            alert(`Erro ao criar ${type === 'unidade' ? 'unidade' : 'classificação'}: ` + (data.error || 'Tente novamente'));
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro na comunicação com o servidor');
    })
    .finally(() => {
        botao.disabled = false;
        botao.textContent = type === 'unidade' ? 'Criar Unidade' : 'Criar Classificação';
    });
}
