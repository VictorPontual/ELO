// Sub-tipo de pesquisa: filtra as opções pelo tipo selecionado e permite criar
// novos sub-tipos vinculados ao tipo atual.
document.addEventListener('DOMContentLoaded', function () {
    const tipoSelect = document.getElementById('id_tipo_pesq_select');
    const subSelect = document.getElementById('id_sub_tipo_pesq_select');
    if (!tipoSelect || !subSelect) return;

    const NEW_VALUE = '__criar_novo_sub_tipo__';
    const modal = document.getElementById('modalCriarSubTipoPesquisa');
    const input = document.getElementById('nomeSubTipoPesquisaInput');
    const botaoCriar = document.getElementById('botaoCriarSubTipoPesquisa');
    const botaoCancelar = document.getElementById('botaoCancelarSubTipoPesquisa');

    // Opção "+ Novo Sub-tipo" ao final.
    const optNovo = document.createElement('option');
    optNovo.value = NEW_VALUE;
    optNovo.textContent = '+ Novo Sub-tipo';
    optNovo.style.fontWeight = 'bold';
    optNovo.style.color = '#0066cc';
    subSelect.appendChild(optNovo);

    function filtrar() {
        const tipo = tipoSelect.value && tipoSelect.value.indexOf('__criar') === -1
            ? tipoSelect.value : '';
        Array.from(subSelect.options).forEach(function (opt) {
            if (opt.value === '' || opt.value === NEW_VALUE) {
                opt.hidden = false;
                return;
            }
            const match = opt.getAttribute('data-tipo') === tipo;
            opt.hidden = !match;
            if (!match && subSelect.value === opt.value) subSelect.value = '';
        });
        optNovo.hidden = !tipo;
    }

    tipoSelect.addEventListener('change', filtrar);
    filtrar();

    if (!modal) return;

    subSelect.addEventListener('change', function () {
        if (this.value === NEW_VALUE) {
            this.value = '';
            const tipo = tipoSelect.value;
            if (!tipo || tipo.indexOf('__criar') !== -1) {
                alert('Selecione primeiro um tipo de pesquisa.');
                return;
            }
            modal.style.display = 'block';
            if (input) input.focus();
        }
    });

    function fechar() {
        modal.style.display = 'none';
        if (input) input.value = '';
    }

    const botaoFechar = modal.querySelector('.close');
    if (botaoFechar) botaoFechar.addEventListener('click', fechar);
    if (botaoCancelar) botaoCancelar.addEventListener('click', fechar);
    window.addEventListener('click', function (event) {
        if (event.target === modal) fechar();
    });

    function criar() {
        const nome = (input.value || '').trim();
        const tipo = tipoSelect.value;
        if (!nome) {
            alert('Digite o nome do sub-tipo.');
            return;
        }
        botaoCriar.disabled = true;
        botaoCriar.textContent = 'Criando...';
        const params = new URLSearchParams();
        params.append('nome_sub_tipo', nome);
        params.append('tipo', tipo);
        fetch(window.urlCriarSubTipoPesquisa, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: params,
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.success) {
                    const opt = document.createElement('option');
                    opt.value = data.id;
                    opt.textContent = data.nome;
                    opt.setAttribute('data-tipo', data.tipo);
                    subSelect.insertBefore(opt, optNovo);
                    subSelect.value = data.id;
                    fechar();
                } else {
                    alert('Erro ao criar sub-tipo: ' + (data.error || 'Tente novamente'));
                }
            })
            .catch(function () { alert('Erro na comunicação com o servidor'); })
            .finally(function () {
                botaoCriar.disabled = false;
                botaoCriar.textContent = 'Criar Sub-tipo';
            });
    }

    if (botaoCriar) botaoCriar.addEventListener('click', criar);
    if (input) {
        input.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') criar();
        });
    }
});
