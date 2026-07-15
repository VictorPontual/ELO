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

    function buildBarChart(id, labels, values, color, horizontal = false) {
        const element = document.getElementById(id);
        if (!element) return;

        new Chart(element, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: color,
                    borderRadius: 8,
                    maxBarThickness: 38,
                }],
            },
            options: {
                indexAxis: horizontal ? 'y' : 'x',
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                        grid: { color: 'rgba(88, 97, 116, 0.15)' },
                    },
                    x: {
                        grid: { display: false },
                    },
                },
            },
        });
    }

    function buildLineChart(id, labels, values) {
        const element = document.getElementById(id);
        if (!element) return;

        new Chart(element, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Aprovados',
                    data: values,
                    borderColor: palette.cyan,
                    backgroundColor: palette.cyanSoft,
                    fill: true,
                    tension: 0.32,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                }],
            },
            options: {
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                        grid: { color: 'rgba(88, 97, 116, 0.15)' },
                    },
                    x: {
                        grid: { display: false },
                    },
                },
            },
        });
    }

    function buildDoughnutChart(id, labels, values, colors) {
        const element = document.getElementById(id);
        if (!element) return;

        new Chart(element, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 0,
                }],
            },
            options: {
                maintainAspectRatio: false,
                cutout: '62%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            boxHeight: 8,
                            boxWidth: 8,
                        },
                    },
                },
            },
        });
    }

    buildLineChart('chartAnual', chartsData.anual.labels, chartsData.anual.values);
    buildBarChart('chartTrimestral', chartsData.trimestral.labels, chartsData.trimestral.values, palette.greenSoft);
    if (chartsData.bimestral) {
        buildBarChart('chartBimestral', chartsData.bimestral.labels, chartsData.bimestral.values, palette.cyanSoft);
    }
    buildBarChart('chartTipo', chartsData.tipo_pesquisa.labels, chartsData.tipo_pesquisa.values, palette.orangeSoft, true);
    buildBarChart('chartClassificacao', chartsData.classificacao.labels, chartsData.classificacao.values, palette.slateSoft, true);

    buildDoughnutChart(
        'chartTecnologico',
        chartsData.tecnologico.labels,
        chartsData.tecnologico.values,
        [palette.cyan, '#d7e7ed']
    );
    buildDoughnutChart(
        'chartMulticentrico',
        chartsData.multicentrico.labels,
        chartsData.multicentrico.values,
        [palette.green, '#dceee6']
    );
    buildDoughnutChart(
        'chartIntegracao',
        chartsData.integracao.labels,
        chartsData.integracao.values,
        [palette.orange, '#f4e5d2']
    );
});
