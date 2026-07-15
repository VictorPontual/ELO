function abrirModal(projetoId) {
    const modal = document.getElementById(`modal-${projetoId}`);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function fecharModal(projetoId) {
    const modal = document.getElementById(`modal-${projetoId}`);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Adicionar event listeners quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Botões de abrir modal
    const botoesDetalhes = document.querySelectorAll('.btn-detalhes');
    botoesDetalhes.forEach(botao => {
        botao.addEventListener('click', function() {
            const projetoId = this.getAttribute('data-projeto-id');
            abrirModal(projetoId);
        });
    });
    
    // Botões de fechar modal
    const botoesFechar = document.querySelectorAll('.close');
    botoesFechar.forEach(botao => {
        botao.addEventListener('click', function() {
            const projetoId = this.getAttribute('data-projeto-id');
            fecharModal(projetoId);
        });
    });
    
    // Botões de editar
    const botoesEditar = document.querySelectorAll('.btn-edit');
    botoesEditar.forEach(botao => {
        botao.addEventListener('click', function() {
            const projetoId = this.getAttribute('data-projeto-id');
            window.location.href = `/projetos/editar/${projetoId}/`;
        });
    });
});

// ---------------------------------------------------------------------------
// Busca + filtros combináveis da lista de projetos.
// ---------------------------------------------------------------------------
(function () {
    const CAMPOS = {
        titulo: { label: 'Título', tipo: 'texto', attr: 'titulo' },
        lider: { label: 'Pesquisador principal', tipo: 'texto', attr: 'lider' },
        tipo: { label: 'Tipo de pesquisa', tipo: 'lista', attr: 'tipo' },
        especialidade: { label: 'Especialidade', tipo: 'lista', attr: 'especialidade' },
        instituicao: { label: 'Instituição', tipo: 'lista', attr: 'instituicao' },
        classificacao: { label: 'Classificação', tipo: 'lista', attr: 'classificacao' },
    };

    document.addEventListener('DOMContentLoaded', function () {
        const busca = document.getElementById('busca-projetos');
        if (!busca) return; // página sem projetos

        const linhas = Array.from(document.querySelectorAll('.linha-projeto'));
        const btnAbrir = document.getElementById('btn-abrir-filtros');
        const painel = document.getElementById('painel-filtros');
        const selCampo = document.getElementById('filtro-campo');
        const selValor = document.getElementById('filtro-valor-select');
        const inputValor = document.getElementById('filtro-valor-input');
        const btnAplicar = document.getElementById('btn-aplicar-filtro');
        const filtrosAtivos = document.getElementById('filtros-ativos');
        const contador = document.getElementById('busca-contador');
        const semResultados = document.getElementById('sem-resultados');
        const tabela = document.querySelector('table');

        const ativos = []; // { campo, attr, valor, label, tipo }

        function valoresDistintos(attr) {
            const set = new Set();
            linhas.forEach(function (linha) {
                const bruto = (linha.dataset[attr] || '').trim();
                if (!bruto) return;
                bruto.split(' | ').forEach(function (parte) {
                    const v = parte.trim();
                    if (v) set.add(v);
                });
            });
            return Array.from(set).sort(function (a, b) { return a.localeCompare(b); });
        }

        function atualizarEntradaValor() {
            const cfg = CAMPOS[selCampo.value];
            if (cfg.tipo === 'texto') {
                selValor.hidden = true;
                inputValor.hidden = false;
                inputValor.value = '';
            } else {
                inputValor.hidden = true;
                selValor.hidden = false;
                selValor.innerHTML = '';
                valoresDistintos(cfg.attr).forEach(function (v) {
                    const opt = document.createElement('option');
                    opt.value = v;
                    opt.textContent = v;
                    selValor.appendChild(opt);
                });
                if (!selValor.options.length) {
                    const opt = document.createElement('option');
                    opt.value = '';
                    opt.textContent = '(sem valores)';
                    selValor.appendChild(opt);
                }
            }
        }

        function renderChips() {
            filtrosAtivos.innerHTML = '';
            ativos.forEach(function (f, idx) {
                const chip = document.createElement('span');
                chip.className = 'chip-filtro';
                const texto = document.createElement('span');
                texto.textContent = f.label + ': ' + f.valor;
                const x = document.createElement('button');
                x.type = 'button';
                x.className = 'chip-filtro__x';
                x.setAttribute('aria-label', 'Remover filtro');
                x.textContent = '✕';
                x.addEventListener('click', function () {
                    ativos.splice(idx, 1);
                    renderChips();
                    aplicar();
                });
                chip.appendChild(texto);
                chip.appendChild(x);
                filtrosAtivos.appendChild(chip);
            });
        }

        function linhaPassaFacetas(linha) {
            // Agrupa filtros por atributo: OR dentro do grupo, AND entre grupos.
            const grupos = {};
            ativos.forEach(function (f) {
                (grupos[f.attr] = grupos[f.attr] || []).push(f);
            });
            return Object.keys(grupos).every(function (attr) {
                const valorLinha = (linha.dataset[attr] || '').toLowerCase();
                return grupos[attr].some(function (f) {
                    const alvo = f.valor.toLowerCase();
                    return f.tipo === 'texto'
                        ? valorLinha.indexOf(alvo) !== -1
                        : valorLinha.split(' | ').indexOf(alvo) !== -1;
                });
            });
        }

        function aplicar() {
            const termo = busca.value.trim().toLowerCase();
            let visiveis = 0;
            linhas.forEach(function (linha) {
                const alvoBusca = [linha.dataset.titulo, linha.dataset.lider, linha.dataset.tipo]
                    .join(' ');
                const passaBusca = !termo || alvoBusca.indexOf(termo) !== -1;
                const passaFacetas = linhaPassaFacetas(linha);
                const mostrar = passaBusca && passaFacetas;
                linha.style.display = mostrar ? '' : 'none';
                if (mostrar) visiveis += 1;
            });
            if (contador) {
                contador.textContent = visiveis + ' de ' + linhas.length + ' projeto(s)';
            }
            if (semResultados && tabela) {
                const vazio = visiveis === 0;
                semResultados.style.display = vazio ? 'block' : 'none';
                tabela.style.display = vazio ? 'none' : '';
            }
        }

        btnAbrir.addEventListener('click', function (event) {
            event.stopPropagation();
            painel.hidden = !painel.hidden;
            if (!painel.hidden) atualizarEntradaValor();
        });
        // Cliques dentro do painel não fecham (não chegam ao document).
        painel.addEventListener('click', function (event) {
            event.stopPropagation();
        });
        selCampo.addEventListener('change', atualizarEntradaValor);
        btnAplicar.addEventListener('click', function () {
            const cfg = CAMPOS[selCampo.value];
            const valor = (cfg.tipo === 'texto' ? inputValor.value : selValor.value).trim();
            if (!valor) return;
            const jaExiste = ativos.some(function (f) {
                return f.attr === cfg.attr && f.valor.toLowerCase() === valor.toLowerCase();
            });
            if (!jaExiste) {
                ativos.push({ campo: selCampo.value, attr: cfg.attr, valor: valor, label: cfg.label, tipo: cfg.tipo });
                renderChips();
                aplicar();
            }
            painel.hidden = true;
        });
        busca.addEventListener('input', aplicar);

        // Fecha o painel ao clicar em qualquer lugar fora dele.
        document.addEventListener('click', function () {
            if (!painel.hidden) painel.hidden = true;
        });
        // Fecha com a tecla Esc.
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && !painel.hidden) painel.hidden = true;
        });

        aplicar();
    });
})();

// Fechar modal ao clicar fora dele
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Fechar modal com tecla ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (modal.style.display === 'block') {
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    }
});
