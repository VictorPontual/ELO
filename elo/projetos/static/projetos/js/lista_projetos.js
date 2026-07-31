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
    // Campos filtráveis. tipo: 'texto' (contém), 'lista' (valor exato de um
    // conjunto) ou 'range' (intervalo de/até; subtipo 'data' ou 'numero').
    const CAMPOS = {
        titulo:        { label: 'Título', tipo: 'texto', attr: 'titulo' },
        lider:         { label: 'Pesquisador principal', tipo: 'texto', attr: 'lider' },
        tipo:          { label: 'Tipo de pesquisa', tipo: 'lista', attr: 'tipo' },
        subtipo:       { label: 'Sub-tipo de pesquisa', tipo: 'lista', attr: 'subtipo' },
        especialidade: { label: 'Especialidade', tipo: 'lista', attr: 'especialidade' },
        instituicao:   { label: 'Instituição', tipo: 'lista', attr: 'instituicao' },
        classificacao: { label: 'Classificação', tipo: 'lista', attr: 'classificacao' },
        classinst:     { label: 'Classificação institucional', tipo: 'lista', attr: 'classinst' },
        fomento:       { label: 'Tipo de fomento', tipo: 'lista', attr: 'fomento' },
        provedor:      { label: 'Provedor de fomento', tipo: 'lista', attr: 'provedor' },
        parecer:       { label: 'Parecer CEP', tipo: 'lista', attr: 'parecer' },
        multicentrico: { label: 'Multicêntrico', tipo: 'lista', attr: 'multicentrico' },
        alerta:        { label: 'Alerta', tipo: 'lista', attr: 'alerta' },
        aprovacao:     { label: 'Data de aprovação institucional', tipo: 'range', subtipo: 'data', attr: 'aprovacao' },
        parecercep:    { label: 'Data do parecer CEP', tipo: 'range', subtipo: 'data', attr: 'parecercep' },
    };

    // Minúsculas + sem acentos, para comparação/busca tolerante.
    function normalizar(t) {
        return (t || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    }

    document.addEventListener('DOMContentLoaded', function () {
        const busca = document.getElementById('busca-projetos');
        if (!busca) return; // página sem projetos

        const linhas = Array.from(document.querySelectorAll('.linha-projeto'));
        const btnAbrir = document.getElementById('btn-abrir-filtros');
        const painel = document.getElementById('painel-filtros');
        const selCampo = document.getElementById('filtro-campo');
        const selValor = document.getElementById('filtro-valor-select');
        const inputValor = document.getElementById('filtro-valor-input');
        const rangeBox = document.getElementById('filtro-valor-range');
        const rangeMin = document.getElementById('filtro-range-min');
        const rangeMax = document.getElementById('filtro-range-max');
        const btnAplicar = document.getElementById('btn-aplicar-filtro');
        const filtrosAtivos = document.getElementById('filtros-ativos');
        const contador = document.getElementById('busca-contador');
        const semResultados = document.getElementById('sem-resultados');
        const tabela = document.querySelector('table');
        const sugestoesBox = document.getElementById('busca-sugestoes');

        const ativos = []; // { campo, attr, tipo, valor, label, [min,max,subtipo] }

        // Preenche o seletor de campos a partir de CAMPOS (fonte única).
        selCampo.innerHTML = '';
        Object.keys(CAMPOS).forEach(function (chave) {
            const opt = document.createElement('option');
            opt.value = chave;
            opt.textContent = CAMPOS[chave].label;
            selCampo.appendChild(opt);
        });

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
            return Array.from(set).sort(function (a, b) { return a.localeCompare(b, 'pt-BR'); });
        }

        function atualizarEntradaValor() {
            const cfg = CAMPOS[selCampo.value];
            selValor.hidden = cfg.tipo !== 'lista';
            inputValor.hidden = cfg.tipo !== 'texto';
            rangeBox.hidden = cfg.tipo !== 'range';

            if (cfg.tipo === 'texto') {
                inputValor.value = '';
            } else if (cfg.tipo === 'lista') {
                selValor.innerHTML = '';
                const valores = valoresDistintos(cfg.attr);
                valores.forEach(function (v) {
                    const opt = document.createElement('option');
                    opt.value = v;
                    opt.textContent = v;
                    selValor.appendChild(opt);
                });
                if (!valores.length) {
                    const opt = document.createElement('option');
                    opt.value = '';
                    opt.textContent = '(sem valores)';
                    selValor.appendChild(opt);
                }
            } else { // range
                const tipoInput = cfg.subtipo === 'numero' ? 'number' : 'date';
                rangeMin.type = tipoInput;
                rangeMax.type = tipoInput;
                rangeMin.value = '';
                rangeMax.value = '';
            }
        }

        function fmtData(iso) {
            const p = (iso || '').split('-'); // YYYY-MM-DD -> DD/MM/YYYY
            return p.length === 3 ? p[2] + '/' + p[1] + '/' + p[0] : iso;
        }

        function rotuloRange(cfg, min, max) {
            const fmt = cfg.subtipo === 'data' ? fmtData : function (v) { return v; };
            if (min && max) return 'de ' + fmt(min) + ' até ' + fmt(max);
            if (min) return 'a partir de ' + fmt(min);
            if (max) return 'até ' + fmt(max);
            return '';
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

        function itemCasa(f, linha) {
            const raw = (linha.dataset[f.attr] || '').trim();
            if (f.tipo === 'range') {
                if (!raw) return false;
                if (f.subtipo === 'numero') {
                    const n = parseFloat(String(raw).replace(',', '.'));
                    if (isNaN(n)) return false;
                    if (f.min !== '' && n < parseFloat(f.min)) return false;
                    if (f.max !== '' && n > parseFloat(f.max)) return false;
                    return true;
                }
                // data: comparação lexicográfica de ISO (YYYY-MM-DD) funciona.
                if (f.min && raw < f.min) return false;
                if (f.max && raw > f.max) return false;
                return true;
            }
            const valorLinha = normalizar(raw);
            const alvo = normalizar(f.valor);
            return f.tipo === 'texto'
                ? valorLinha.indexOf(alvo) !== -1
                : valorLinha.split(' | ').indexOf(alvo) !== -1;
        }

        function linhaPassaFacetas(linha) {
            // Agrupa filtros por atributo: OR dentro do grupo, AND entre grupos.
            const grupos = {};
            ativos.forEach(function (f) {
                (grupos[f.attr] = grupos[f.attr] || []).push(f);
            });
            return Object.keys(grupos).every(function (attr) {
                return grupos[attr].some(function (f) { return itemCasa(f, linha); });
            });
        }

        function aplicar() {
            const termo = normalizar(busca.value.trim());
            let visiveis = 0;
            linhas.forEach(function (linha) {
                const alvoBusca = normalizar(
                    [linha.dataset.titulo, linha.dataset.lider, linha.dataset.tipo].join(' ')
                );
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

        // --- Autocomplete da busca ---------------------------------------
        const poolSugestoes = (function () {
            const set = new Set();
            linhas.forEach(function (l) {
                [l.dataset.titulo, l.dataset.lider, l.dataset.tipo].forEach(function (v) {
                    v = (v || '').trim();
                    if (v) set.add(v);
                });
            });
            return Array.from(set);
        })();
        let sugestaoAtiva = -1;

        function fecharSugestoes() {
            if (!sugestoesBox) return;
            sugestoesBox.hidden = true;
            sugestoesBox.innerHTML = '';
            sugestaoAtiva = -1;
        }

        function mostrarSugestoes() {
            if (!sugestoesBox) return;
            const termo = normalizar(busca.value.trim());
            if (!termo) { fecharSugestoes(); return; }
            const casam = poolSugestoes
                .filter(function (v) { return normalizar(v).indexOf(termo) !== -1; })
                .slice(0, 8);
            if (!casam.length) { fecharSugestoes(); return; }
            sugestoesBox.innerHTML = '';
            casam.forEach(function (v) {
                const li = document.createElement('li');
                li.className = 'busca-sugestao';
                li.textContent = v;
                // mousedown (antes do blur do input) evita fechar antes do clique.
                li.addEventListener('mousedown', function (e) {
                    e.preventDefault();
                    busca.value = v;
                    fecharSugestoes();
                    aplicar();
                });
                sugestoesBox.appendChild(li);
            });
            sugestoesBox.hidden = false;
            sugestaoAtiva = -1;
        }

        // --- Eventos ------------------------------------------------------
        btnAbrir.addEventListener('click', function (event) {
            event.stopPropagation();
            painel.hidden = !painel.hidden;
            if (!painel.hidden) atualizarEntradaValor();
        });
        painel.addEventListener('click', function (event) { event.stopPropagation(); });
        selCampo.addEventListener('change', atualizarEntradaValor);

        btnAplicar.addEventListener('click', function () {
            const cfg = CAMPOS[selCampo.value];
            if (cfg.tipo === 'range') {
                const min = rangeMin.value.trim();
                const max = rangeMax.value.trim();
                if (!min && !max) return;
                ativos.push({
                    campo: selCampo.value, attr: cfg.attr, tipo: 'range',
                    subtipo: cfg.subtipo, min: min, max: max,
                    valor: rotuloRange(cfg, min, max), label: cfg.label,
                });
                renderChips();
                aplicar();
                painel.hidden = true;
                return;
            }
            const valor = (cfg.tipo === 'texto' ? inputValor.value : selValor.value).trim();
            if (!valor) return;
            const jaExiste = ativos.some(function (f) {
                return f.attr === cfg.attr && f.tipo !== 'range'
                    && normalizar(f.valor) === normalizar(valor);
            });
            if (!jaExiste) {
                ativos.push({ campo: selCampo.value, attr: cfg.attr, valor: valor, label: cfg.label, tipo: cfg.tipo });
                renderChips();
                aplicar();
            }
            painel.hidden = true;
        });

        busca.addEventListener('input', function () { aplicar(); mostrarSugestoes(); });
        busca.addEventListener('focus', mostrarSugestoes);
        busca.addEventListener('blur', function () { setTimeout(fecharSugestoes, 120); });
        busca.addEventListener('keydown', function (event) {
            if (sugestoesBox.hidden) return;
            const itens = Array.from(sugestoesBox.querySelectorAll('.busca-sugestao'));
            if (!itens.length) return;
            if (event.key === 'ArrowDown') {
                event.preventDefault();
                sugestaoAtiva = (sugestaoAtiva + 1) % itens.length;
            } else if (event.key === 'ArrowUp') {
                event.preventDefault();
                sugestaoAtiva = (sugestaoAtiva - 1 + itens.length) % itens.length;
            } else if (event.key === 'Enter' && sugestaoAtiva >= 0) {
                event.preventDefault();
                busca.value = itens[sugestaoAtiva].textContent;
                fecharSugestoes();
                aplicar();
                return;
            } else if (event.key === 'Escape') {
                fecharSugestoes();
                return;
            } else {
                return;
            }
            itens.forEach(function (it, i) { it.classList.toggle('ativa', i === sugestaoAtiva); });
        });

        // Fecha o painel ao clicar fora dele.
        document.addEventListener('click', function () {
            if (!painel.hidden) painel.hidden = true;
        });
        // Fecha painel/sugestões com Esc.
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && !painel.hidden) painel.hidden = true;
        });

        aplicar();
    });
})();

// ---------------------------------------------------------------------------
// Popup de cobrança: ao clicar num ícone de alerta, abre a prévia e permite
// enviar a cobrança (reaproveita a view enviar_cobranca_alerta).
// ---------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('modal-cobranca');
    if (!modal) return;
    const form = document.getElementById('form-cobranca');
    const semPermissao = document.getElementById('cobranca-sem-permissao');

    function abrir(botao) {
        document.getElementById('cobranca-tipo').textContent = botao.dataset.tipo || 'Cobrança';
        document.getElementById('cobranca-titulo').textContent = botao.dataset.titulo || '';
        document.getElementById('cobranca-destinatario').textContent =
            botao.dataset.destinatario || '(pesquisador sem e-mail cadastrado)';
        document.getElementById('cobranca-assunto').value = botao.dataset.assunto || '';
        document.getElementById('cobranca-mensagem').value = botao.dataset.mensagem || '';

        const action = botao.dataset.action || '';
        if (action) {
            form.action = action;
            form.style.display = '';
            if (semPermissao) semPermissao.style.display = 'none';
        } else {
            // Sem permissão de envio: mostra só a prévia.
            form.style.display = 'none';
            if (semPermissao) semPermissao.style.display = '';
        }

        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    function fechar() {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    document.querySelectorAll('.btn-cobranca').forEach(function (botao) {
        botao.addEventListener('click', function () { abrir(botao); });
    });

    const fecharBtn = document.getElementById('fechar-cobranca');
    const cancelar = document.getElementById('cancelar-cobranca');
    if (fecharBtn) fecharBtn.addEventListener('click', fechar);
    if (cancelar) cancelar.addEventListener('click', fechar);
});

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
