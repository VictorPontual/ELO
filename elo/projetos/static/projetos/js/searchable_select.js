// Transforma qualquer <select data-searchable> em um campo de busca com
// correspondência por semelhança (ignora acentos/maiúsculas, aceita subsequência
// e pequenas diferenças de digitação). Sem dependências externas.
(function () {
    'use strict';

    function normalizar(texto) {
        return (texto || '')
            .toString()
            .toLowerCase()
            .normalize('NFD')
            .replace(/[̀-ͯ]/g, '')
            .trim();
    }

    // Distância de Levenshtein (limitada) para ranquear semelhança.
    function levenshtein(a, b) {
        if (a === b) return 0;
        if (!a.length) return b.length;
        if (!b.length) return a.length;
        let anterior = [];
        for (let j = 0; j <= b.length; j++) anterior[j] = j;
        for (let i = 1; i <= a.length; i++) {
            let atual = [i];
            for (let j = 1; j <= b.length; j++) {
                const custo = a[i - 1] === b[j - 1] ? 0 : 1;
                atual[j] = Math.min(
                    anterior[j] + 1,
                    atual[j - 1] + 1,
                    anterior[j - 1] + custo
                );
            }
            anterior = atual;
        }
        return anterior[b.length];
    }

    function ehSubsequencia(consulta, alvo) {
        let i = 0;
        for (let j = 0; j < alvo.length && i < consulta.length; j++) {
            if (consulta[i] === alvo[j]) i++;
        }
        return i === consulta.length;
    }

    // Retorna um score (maior = melhor) ou null se não corresponder.
    function pontuar(consulta, alvo) {
        if (!consulta) return 0;
        const c = normalizar(consulta);
        const a = normalizar(alvo);
        if (!a) return null;
        const idx = a.indexOf(c);
        if (idx !== -1) return 1000 - idx; // substring: quanto mais no início, melhor
        if (ehSubsequencia(c, a)) return 500 - (a.length - c.length);
        // Tolerância a erros de digitação por palavra.
        let melhor = null;
        a.split(/\s+/).forEach(function (palavra) {
            const dist = levenshtein(c, palavra);
            const limite = Math.max(1, Math.floor(palavra.length / 3));
            if (dist <= limite) {
                const score = 200 - dist * 10;
                if (melhor === null || score > melhor) melhor = score;
            }
        });
        return melhor;
    }

    function enhance(select) {
        if (select.dataset.searchableReady) return;
        select.dataset.searchableReady = '1';

        const placeholder = select.dataset.placeholder || 'Digite para buscar...';
        const opcoes = Array.from(select.options).map(function (opt) {
            return { value: opt.value, label: opt.textContent.trim(), vazia: opt.value === '' };
        });

        const wrapper = document.createElement('div');
        wrapper.className = 'searchable-select';

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'searchable-select__input ' + (select.className || '');
        input.setAttribute('autocomplete', 'off');
        input.placeholder = placeholder;

        const lista = document.createElement('ul');
        lista.className = 'searchable-select__list';
        lista.hidden = true;

        select.parentNode.insertBefore(wrapper, select);
        wrapper.appendChild(input);
        wrapper.appendChild(lista);
        wrapper.appendChild(select);
        select.classList.add('searchable-select__native');

        let indiceAtivo = -1;
        let itensVisiveis = [];

        function textoSelecionado() {
            const sel = opcoes.find(function (o) { return o.value === select.value; });
            return sel && !sel.vazia ? sel.label : '';
        }
        input.value = textoSelecionado();

        function fechar() {
            lista.hidden = true;
            indiceAtivo = -1;
        }

        function render(consulta) {
            lista.innerHTML = '';
            const candidatos = [];
            opcoes.forEach(function (opt) {
                if (opt.vazia) return;
                const score = pontuar(consulta, opt.label);
                if (score !== null) candidatos.push({ opt: opt, score: score });
            });
            candidatos.sort(function (x, y) {
                if (y.score !== x.score) return y.score - x.score;
                return x.opt.label.localeCompare(y.opt.label);
            });
            itensVisiveis = candidatos.slice(0, 50);
            if (!itensVisiveis.length) {
                const li = document.createElement('li');
                li.className = 'searchable-select__empty';
                li.textContent = 'Nenhum resultado';
                lista.appendChild(li);
            } else {
                itensVisiveis.forEach(function (item, i) {
                    const li = document.createElement('li');
                    li.className = 'searchable-select__item';
                    li.textContent = item.opt.label;
                    li.dataset.value = item.opt.value;
                    li.addEventListener('mousedown', function (e) {
                        e.preventDefault();
                        escolher(item.opt);
                    });
                    li.addEventListener('mouseenter', function () {
                        marcar(i);
                    });
                    lista.appendChild(li);
                });
            }
            lista.hidden = false;
            indiceAtivo = -1;
        }

        function marcar(i) {
            const filhos = lista.querySelectorAll('.searchable-select__item');
            filhos.forEach(function (el, idx) {
                el.classList.toggle('is-active', idx === i);
            });
            indiceAtivo = i;
        }

        function escolher(opt) {
            select.value = opt.value;
            input.value = opt.label;
            select.dispatchEvent(new Event('change', { bubbles: true }));
            fechar();
        }

        input.addEventListener('focus', function () {
            render(input.value);
        });
        input.addEventListener('input', function () {
            select.value = '';
            render(input.value);
        });
        input.addEventListener('keydown', function (e) {
            if (lista.hidden && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
                render(input.value);
                return;
            }
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                marcar(Math.min(indiceAtivo + 1, itensVisiveis.length - 1));
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                marcar(Math.max(indiceAtivo - 1, 0));
            } else if (e.key === 'Enter') {
                if (!lista.hidden && indiceAtivo >= 0 && itensVisiveis[indiceAtivo]) {
                    e.preventDefault();
                    escolher(itensVisiveis[indiceAtivo].opt);
                }
            } else if (e.key === 'Escape') {
                fechar();
            }
        });
        input.addEventListener('blur', function () {
            // Se nada foi selecionado e o texto não corresponde exatamente, limpa.
            setTimeout(function () {
                if (!select.value) input.value = '';
                else input.value = textoSelecionado();
                fechar();
            }, 150);
        });
    }

    function init(raiz) {
        (raiz || document).querySelectorAll('select[data-searchable]').forEach(enhance);
    }

    document.addEventListener('DOMContentLoaded', function () { init(document); });
    window.SearchableSelect = { init: init, enhance: enhance };
})();
