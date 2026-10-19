document.addEventListener('DOMContentLoaded', function () {
    const dataElement = document.getElementById('dashboard-charts-data');
    if (!dataElement || typeof Chart === 'undefined') {
        return;
    }

    const chartsData = JSON.parse(dataElement.textContent);

    const palette = {
        cyan: '#00a3a3',
        cyanSoft: 'rgba(0, 163, 163, 0.55)',
        orange: '#d78124',
        grid: 'rgba(88, 97, 116, 0.15)',
    };

    const formatos = {
        num: function (v) { return Number(v).toLocaleString('pt-BR'); },
        pct: function (v) { return v + '%'; },
        brl: function (v) { return 'R$ ' + Math.round(v).toLocaleString('pt-BR'); },
    };

    // Rótulos curtos para o eixo (o tooltip mantém o valor completo).
    const formatosEixo = {
        brl: function (v) {
            if (Math.abs(v) >= 1e6) return 'R$ ' + (v / 1e6).toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + ' mi';
            if (Math.abs(v) >= 1e3) return 'R$ ' + (v / 1e3).toLocaleString('pt-BR', { maximumFractionDigits: 0 }) + ' mil';
            return 'R$ ' + v;
        },
    };

    function encurtar(texto, max) {
        texto = String(texto);
        return texto.length > max ? texto.slice(0, max - 1) + '…' : texto;
    }

    function mostrarVazio(canvas) {
        const aviso = document.createElement('p');
        aviso.className = 'vazio';
        aviso.textContent = 'Sem dados para exibir.';
        canvas.parentElement.replaceWith(aviso);
    }

    // --- Barras horizontais: <canvas data-serie="chave" data-formato="num|pct|brl"> ---
    function barrasHorizontais(canvas, serie, fmt, fmtEixo) {
        // Altura proporcional ao número de categorias.
        canvas.parentElement.style.height = Math.max(120, serie.labels.length * 30 + 40) + 'px';
        // Rótulos ocupam no máximo ~metade da largura do card.
        const maxRotulo = Math.max(14, Math.round(canvas.parentElement.clientWidth / 14));
        return new Chart(canvas, {
            type: 'bar',
            data: {
                labels: serie.labels,
                datasets: [{
                    data: serie.values,
                    backgroundColor: palette.cyanSoft,
                    borderRadius: 6,
                    maxBarThickness: 22,
                }],
            },
            options: {
                indexAxis: 'y',
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            title: function (itens) { return serie.labels[itens[0].dataIndex]; },
                            label: function (ctx) { return fmt(ctx.parsed.x); },
                        },
                    },
                },
                scales: {
                    x: { beginAtZero: true, ticks: { precision: 0, maxRotation: 0, callback: fmtEixo || fmt }, grid: { color: palette.grid } },
                    y: {
                        grid: { display: false },
                        ticks: {
                            autoSkip: false,
                            callback: function (valor) { return encurtar(this.getLabelForValue(valor), maxRotulo); },
                        },
                    },
                },
            },
        });
    }

    document.querySelectorAll('canvas[data-serie]').forEach(function (canvas) {
        const serie = chartsData[canvas.dataset.serie];
        if (!serie || !serie.labels.length) {
            mostrarVazio(canvas);
            return;
        }
        const formato = canvas.dataset.formato;
        barrasHorizontais(canvas, serie, formatos[formato] || formatos.num, formatosEixo[formato]);
    });

    // --- Painel: aprovação institucional por período (Trimestre / Bimestre) ---
    const canvasPeriodo = document.getElementById('chartPeriodo');
    const periodo = chartsData.periodo;
    if (!canvasPeriodo || !periodo) {
        return;
    }

    const ROTULOS = {
        t: ['1º tri', '2º tri', '3º tri', '4º tri'],
        b: ['jan–fev', 'mar–abr', 'mai–jun', 'jul–ago', 'set–out', 'nov–dez'],
    };
    const ano = canvasPeriodo.dataset.ano;
    const dadosAno = periodo.anos[ano] || { t: [0, 0, 0, 0], b: [0, 0, 0, 0, 0, 0] };
    const totalEl = document.getElementById('periodo-total');
    let chartPeriodo = null;

    function renderPeriodo(gr) {
        const valores = dadosAno[gr];
        const atual = ano === periodo.atual.ano ? periodo.atual[gr] : -1;
        const cores = valores.map(function (_, i) { return i === atual ? palette.orange : palette.cyan; });
        if (chartPeriodo) chartPeriodo.destroy();
        chartPeriodo = new Chart(canvasPeriodo, {
            type: 'bar',
            data: {
                labels: ROTULOS[gr].map(function (r, i) { return i === atual ? r + ' (em curso)' : r; }),
                datasets: [{ label: 'Aprovações', data: valores, backgroundColor: cores, borderRadius: 8, maxBarThickness: 64 }],
            },
            options: {
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: palette.grid } },
                    x: { grid: { display: false } },
                },
            },
        });
        if (totalEl) {
            totalEl.textContent = valores.reduce(function (a, b) { return a + b; }, 0).toLocaleString('pt-BR');
        }
    }

    const botoes = Array.from(document.querySelectorAll('.seg-btn[data-gr]'));
    botoes.forEach(function (btn) {
        btn.addEventListener('click', function () {
            botoes.forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
            renderPeriodo(btn.dataset.gr);
        });
    });
    renderPeriodo('t');
});
