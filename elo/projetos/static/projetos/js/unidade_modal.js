// Modal para criar nova unidade
document.addEventListener('DOMContentLoaded', function() {
    const unidadeSelect = document.getElementById('id_unidade_select');
    
    if (!unidadeSelect) return;
    
    // Adicionar opção "Criar Nova Unidade" ao topo do select
    const optionCriarNova = document.createElement('option');
    optionCriarNova.value = '__criar_nova__';
    optionCriarNova.textContent = '+ Criar Nova Unidade';
    optionCriarNova.style.fontWeight = 'bold';
    optionCriarNova.style.color = '#0066cc';
    
    // Inserir como primeira opção após o label padrão
    if (unidadeSelect.options.length > 0 && unidadeSelect.options[0].value === '') {
        unidadeSelect.insertBefore(optionCriarNova, unidadeSelect.options[1]);
    } else {
        unidadeSelect.insertBefore(optionCriarNova, unidadeSelect.options[0]);
    }
    
    // Evento de mudança no select
    unidadeSelect.addEventListener('change', function() {
        if (this.value === '__criar_nova__') {
            abrirModalCriarUnidade();
            // Resetar select para a primeira opção
            this.value = '';
        }
    });
    
    function abrirModalCriarUnidade() {
        const modal = document.getElementById('modalCriarUnidade');
        if (modal) {
            modal.style.display = 'block';
            document.getElementById('nomeUnidadeInput').focus();
        }
    }
    
    // Fechar modal
    const botaoFechar = document.querySelector('#modalCriarUnidade .close');
    if (botaoFechar) {
        botaoFechar.addEventListener('click', function() {
            document.getElementById('modalCriarUnidade').style.display = 'none';
        });
    }
    
    // Fechar clicando fora do modal
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('modalCriarUnidade');
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Cancelar
    const botaoCancelar = document.getElementById('botaoCancelarUnidade');
    if (botaoCancelar) {
        botaoCancelar.addEventListener('click', function() {
            document.getElementById('modalCriarUnidade').style.display = 'none';
            document.getElementById('nomeUnidadeInput').value = '';
        });
    }
    
    // Criar unidade
    const botaoCriar = document.getElementById('botaoCriarUnidade');
    if (botaoCriar) {
        botaoCriar.addEventListener('click', criarUnidade);
    }
    
    const inputNome = document.getElementById('nomeUnidadeInput');
    if (inputNome) {
        inputNome.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                criarUnidade();
            }
        });
    }
    
    function criarUnidade() {
        const nomeUnidade = document.getElementById('nomeUnidadeInput').value.trim();
        
        if (!nomeUnidade) {
            alert('Por favor, digite o nome da unidade');
            return;
        }
        
        // Desabilitar botão durante requisição
        botaoCriar.disabled = true;
        botaoCriar.textContent = 'Criando...';
        
        fetch(window.urlCriarUnidade, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: 'nome_unidade=' + encodeURIComponent(nomeUnidade)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Adicionar nova opção ao select
                const novaOpcao = document.createElement('option');
                novaOpcao.value = data.id;
                novaOpcao.textContent = data.nome;
                unidadeSelect.appendChild(novaOpcao);
                
                // Selecionar a nova opção
                unidadeSelect.value = data.id;
                
                // Fechar modal
                document.getElementById('modalCriarUnidade').style.display = 'none';
                document.getElementById('nomeUnidadeInput').value = '';
                
                // Feedback ao usuário
                alert('Unidade criada com sucesso!');
            } else {
                alert('Erro ao criar unidade: ' + (data.error || 'Tente novamente'));
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro na comunicação com o servidor');
        })
        .finally(() => {
            botaoCriar.disabled = false;
            botaoCriar.textContent = 'Criar Unidade';
        });
    }
});
