document.addEventListener('DOMContentLoaded', function () {
    const dataElement = document.getElementById('dashboard-charts-data');
    if (!dataElement) {
        return;
    }

    const chartsData = JSON.parse(dataElement.textContent);

    const palette = {
        cyan: '#00a3a3',
        cyanSoft: 'rgba(0, 163, 163, 0.34)',
        green: '#2e9f70',
        greenSoft: 'rgba(46, 159, 112, 0.55)',
        orange: '#d78124',
        orangeSoft: 'rgba(215, 129, 36, 0.58)',
        slate: '#4f647d',
        slateSoft: 'rgba(79, 100, 125, 0.6)',
    };

    const eixoBase = {
        y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: 'rgba(88, 97, 116, 0.15)' } },
        x: { grid: { display: false } },
    };

    // --- Builders (retornam a instância para permitir destroy/recriação) ---
    function barChart(element, labels, values, color, horizontal) {
        return new Chart(element, {
            type: 'bar',
            data: { labels: labels, datasets: [{ data: values, backgroundColor: color, borderRadius: 8, maxBarThickness: 38 }] },
            options: {
                indexAxis: horizontal ? 'y' : 'x',
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: eixoBase,
            },
        });
    }

    function lineChart(element, labels, values) {
        return new Chart(element, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Aprovados', data: values,
                    borderColor: palette.cyan, backgroundColor: palette.cyanSoft,
                    fill: true, tension: 0.32, pointRadius: 4, pointHoverRadius: 6,
                }],
            },
            options: {
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: eixoBase,
            },
        });
    }

    function doughnutChart(element, labels, values, colors) {
        return new Chart(element, {
            type: 'doughnut',
            data: { labels: labels, datasets: [{ data: values, backgroundColor: colors, borderWidth: 0 }] },
            options: {
                maintainAspectRatio: false,
                cutout: '62%',
                plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, boxHeight: 8, boxWidth: 8 } } },
            },
        });
    }

    // --- Painel A: aprovações ao longo do tempo (Ano / Trimestre / Bimestre) ---
    const elTempo = document.getElementById('chartTempo');
    let chartTempo = null;

    function renderTempo(serie) {
        const d = chartsData[serie];
        if (!elTempo || !d) return;
        if (chartTempo) chartTempo.destroy();
        if (serie === 'anual') {
            chartTempo = lineChart(elTempo, d.labels, d.values);
        } else {
            const cores = { trimestral: palette.greenSoft, bimestral: palette.cyanSoft, andamento: palette.slateSoft };
            chartTempo = barChart(elTempo, d.labels, d.values, cores[serie] || palette.greenSoft, false);
        }
    }

    const botoesSerie = Array.from(document.querySelectorAll('.seg-btn'));
    botoesSerie.forEach(function (btn) {
        btn.addEventListener('click', function () {
            botoesSerie.forEach(function (b) { b.classList.remove('ativo'); });
            btn.classList.add('ativo');
            renderTempo(btn.dataset.serie);
        });
    });
    renderTempo('anual');

    // --- Painel B: distribuição dos projetos (dimensão + por trimestre) ---
    const elDist = document.getElementById('chartDist');
    const selDim = document.getElementById('dist-dim');
    const distTrim = document.getElementById('dist-trim');
    let chartDist = null;

    const TRIM_LABELS = ['1o tri', '2o tri', '3o tri', '4o tri'];
    const TRIM_CORES = [palette.cyanSoft, palette.greenSoft, palette.orangeSoft, palette.slateSoft];
    // Cores das dimensões em rosca (booleanas + tecnológico com 3-4 fatias).
    const ROSCA_CORES = {
        tecnologico: ['#00a3a3', '#d78124', '#4f647d', '#d7e7ed'],
        multicentrico: ['#2e9f70', '#dceee6'],
        integracao: ['#d78124', '#f4e5d2'],
        rede_hubrasil: ['#4f647d', '#e2e6eb'],
    };

    function renderDist() {
        if (!elDist || !selDim) return;
        const dim = selDim.value;
        const d = (chartsData.dist || {})[dim];
        if (!d) return;
        if (chartDist) chartDist.destroy();

        const ehSubAprov = d.tipo === 'sub_aprov';
        // "por trimestre" não se aplica a submetidos x aprovados.
        distTrim.disabled = ehSubAprov;
        distTrim.parentElement.classList.toggle('desabilitado', ehSubAprov);
        const porTrim = distTrim.checked && !ehSubAprov;

        if (ehSubAprov) {
            chartDist = new Chart(elDist, {
                type: 'bar',
                data: {
                    labels: d.labels,
                    datasets: [
                        { label: 'Submetidos', data: d.submetidos, backgroundColor: palette.slateSoft, borderRadius: 6 },
                        { label: 'Aprovados', data: d.aprovados, backgroundColor: palette.greenSoft, borderRadius: 6 },
                    ],
                },
                options: {
                    indexAxis: 'y', maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } }, scales: eixoBase,
                },
            });
        } else if (porTrim) {
            const datasets = d.trimestres.map(function (vals, i) {
                return { label: TRIM_LABELS[i], data: vals, backgroundColor: TRIM_CORES[i], borderRadius: 4 };
            });
            chartDist = new Chart(elDist, {
                type: 'bar',
                data: { labels: d.labels, datasets: datasets },
                options: {
                    indexAxis: 'y', maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } },
                    scales: {
                        x: { stacked: true, beginAtZero: true, ticks: { precision: 0 }, grid: { color: 'rgba(88,97,116,0.15)' } },
                        y: { stacked: true, grid: { display: false } },
                    },
                },
            });
        } else if (d.tipo === 'rosca') {
            chartDist = doughnutChart(elDist, d.labels, d.total, ROSCA_CORES[dim] || [palette.cyan, palette.green, palette.orange, palette.slate]);
        } else {
            chartDist = barChart(elDist, d.labels, d.total, palette.orangeSoft, true);
        }
    }

    if (selDim) {
        selDim.addEventListener('change', renderDist);
        distTrim.addEventListener('change', renderDist);
        renderDist();
    }
});
