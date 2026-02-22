/**
 * dashboard.js  –  Analytics Dashboard page
 * Fetches data from API and renders Chart.js charts
 */

// ─── Chart.js defaults ───────────────────────────────────────
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.plugins.legend.display = false;

const CHART_OPTIONS_BASE = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
        legend: { display: false },
        tooltip: {
            backgroundColor: 'rgba(13,22,38,0.95)',
            borderColor: 'rgba(99,119,173,0.3)',
            borderWidth: 1,
            padding: 12,
            titleColor: '#f1f5f9',
            bodyColor: '#94a3b8',
            displayColors: true,
            cornerRadius: 8
        }
    },
    scales: {
        x: {
            grid: { color: 'rgba(71,85,105,0.2)' },
            ticks: { color: '#64748b', font: { size: 10 }, maxTicksLimit: 10 }
        },
        y: {
            grid: { color: 'rgba(71,85,105,0.2)' },
            ticks: { color: '#64748b', font: { size: 10 } }
        }
    }
};

// ─── Chart registry ──────────────────────────────────────────
const charts = {};

function destroyChart(id) {
    if (charts[id]) { charts[id].destroy(); delete charts[id]; }
}

// ─── Temperature Line Chart ───────────────────────────────────
function renderTempChart(labels, temps) {
    destroyChart('tempChart');
    const ctx = document.getElementById('tempChart').getContext('2d');

    // Gradient fill
    const grad = ctx.createLinearGradient(0, 0, 0, 220);
    grad.addColorStop(0, 'rgba(249,115,22,0.3)');
    grad.addColorStop(1, 'rgba(249,115,22,0)');

    charts.tempChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Temperature (°C)',
                data: temps,
                borderColor: '#f97316',
                borderWidth: 2,
                backgroundColor: grad,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 5,
                pointHoverBackgroundColor: '#f97316'
            }]
        },
        options: {
            ...CHART_OPTIONS_BASE,
            plugins: {
                ...CHART_OPTIONS_BASE.plugins,
                tooltip: {
                    ...CHART_OPTIONS_BASE.plugins.tooltip,
                    callbacks: {
                        label: ctx => ` ${ctx.parsed.y.toFixed(1)} °C`
                    }
                }
            },
            scales: {
                ...CHART_OPTIONS_BASE.scales,
                y: {
                    ...CHART_OPTIONS_BASE.scales.y,
                    ticks: {
                        ...CHART_OPTIONS_BASE.scales.y.ticks,
                        callback: v => v + '°C'
                    }
                }
            }
        }
    });
}

// ─── Rainfall Bar Chart ───────────────────────────────────────
function renderRainfallChart(labels, rainfall) {
    destroyChart('rainfallChart');
    const ctx = document.getElementById('rainfallChart').getContext('2d');

    charts.rainfallChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Rainfall (mm)',
                data: rainfall,
                backgroundColor: rainfall.map(v =>
                    v > 10 ? 'rgba(59,130,246,0.8)' :
                        v > 3 ? 'rgba(56,189,248,0.6)' : 'rgba(56,189,248,0.3)'
                ),
                borderColor: 'rgba(56,189,248,0.4)',
                borderWidth: 1,
                borderRadius: 4,
                borderSkipped: false
            }]
        },
        options: {
            ...CHART_OPTIONS_BASE,
            plugins: {
                ...CHART_OPTIONS_BASE.plugins,
                tooltip: {
                    ...CHART_OPTIONS_BASE.plugins.tooltip,
                    callbacks: { label: ctx => ` ${ctx.parsed.y.toFixed(1)} mm` }
                }
            },
            scales: {
                ...CHART_OPTIONS_BASE.scales,
                y: {
                    ...CHART_OPTIONS_BASE.scales.y,
                    ticks: {
                        ...CHART_OPTIONS_BASE.scales.y.ticks,
                        callback: v => v + ' mm'
                    }
                }
            }
        }
    });
}

// ─── Humidity Area Chart ──────────────────────────────────────
function renderHumidityChart(labels, humidity) {
    destroyChart('humidityChart');
    const ctx = document.getElementById('humidityChart').getContext('2d');

    const grad = ctx.createLinearGradient(0, 0, 0, 220);
    grad.addColorStop(0, 'rgba(52,211,153,0.3)');
    grad.addColorStop(1, 'rgba(52,211,153,0)');

    charts.humidityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Humidity (%)',
                data: humidity,
                borderColor: '#34d399',
                borderWidth: 2,
                backgroundColor: grad,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 5,
                pointHoverBackgroundColor: '#34d399'
            }]
        },
        options: {
            ...CHART_OPTIONS_BASE,
            plugins: {
                ...CHART_OPTIONS_BASE.plugins,
                tooltip: {
                    ...CHART_OPTIONS_BASE.plugins.tooltip,
                    callbacks: { label: ctx => ` ${ctx.parsed.y.toFixed(1)}%` }
                }
            },
            scales: {
                ...CHART_OPTIONS_BASE.scales,
                y: {
                    ...CHART_OPTIONS_BASE.scales.y,
                    min: 0, max: 100,
                    ticks: {
                        ...CHART_OPTIONS_BASE.scales.y.ticks,
                        callback: v => v + '%'
                    }
                }
            }
        }
    });
}

// ─── Pressure Line Chart ──────────────────────────────────────
function renderPressureChart(labels, pressure) {
    destroyChart('pressureChart');
    const ctx = document.getElementById('pressureChart').getContext('2d');

    const grad = ctx.createLinearGradient(0, 0, 0, 220);
    grad.addColorStop(0, 'rgba(167,139,250,0.3)');
    grad.addColorStop(1, 'rgba(167,139,250,0)');

    charts.pressureChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Pressure (hPa)',
                data: pressure,
                borderColor: '#a78bfa',
                borderWidth: 2,
                backgroundColor: grad,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 5,
                pointHoverBackgroundColor: '#a78bfa'
            }]
        },
        options: {
            ...CHART_OPTIONS_BASE,
            plugins: {
                ...CHART_OPTIONS_BASE.plugins,
                tooltip: {
                    ...CHART_OPTIONS_BASE.plugins.tooltip,
                    callbacks: { label: ctx => ` ${ctx.parsed.y.toFixed(1)} hPa` }
                }
            },
            scales: {
                ...CHART_OPTIONS_BASE.scales,
                y: {
                    ...CHART_OPTIONS_BASE.scales.y,
                    ticks: {
                        ...CHART_OPTIONS_BASE.scales.y.ticks,
                        callback: v => v + ' hPa'
                    }
                }
            }
        }
    });
}

// ─── Condition Doughnut Chart ─────────────────────────────────
async function renderConditionChart() {
    try {
        const resp = await fetch('/api/condition-stats');
        if (!resp.ok) return;
        const data = await resp.json();

        destroyChart('conditionChart');
        const ctx = document.getElementById('conditionChart').getContext('2d');

        const labels = Object.keys(data);
        const values = Object.values(data);
        const COLORS = ['#f97316', '#38bdf8', '#a78bfa', '#34d399', '#fbbf24', '#f43f5e'];

        charts.conditionChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: COLORS.slice(0, labels.length).map(c => c + 'cc'),
                    borderColor: COLORS.slice(0, labels.length),
                    borderWidth: 2,
                    hoverOffset: 12
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'right',
                        labels: {
                            color: '#94a3b8',
                            font: { size: 11 },
                            padding: 12,
                            boxWidth: 12, boxHeight: 12,
                            borderRadius: 3
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(13,22,38,0.95)',
                        borderColor: 'rgba(99,119,173,0.3)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: ctx => {
                                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = ((ctx.parsed / total) * 100).toFixed(1);
                                return ` ${ctx.label}: ${ctx.parsed} days (${pct}%)`;
                            }
                        }
                    }
                },
                cutout: '65%'
            }
        });
    } catch (err) {
        console.error('Condition chart error:', err);
    }
}

// ─── Update summary metrics ───────────────────────────────────
function updateMetrics(data) {
    const avg = arr => arr.length
        ? (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1)
        : '--';

    const el = id => document.getElementById(id);
    const set = (id, val) => { if (el(id)) el(id).textContent = val; };

    set('mc-avg-temp', avg(data.temperature));
    set('mc-avg-hum', avg(data.humidity));
    set('mc-avg-rain', avg(data.rainfall));
    set('mc-avg-pres', avg(data.pressure));
}

// ─── Slice data by selected days ──────────────────────────────
function sliceData(data, days) {
    const n = Math.min(days, data.dates.length);
    return {
        dates: data.dates.slice(-n),
        temperature: data.temperature.slice(-n),
        humidity: data.humidity.slice(-n),
        rainfall: data.rainfall.slice(-n),
        pressure: data.pressure.slice(-n),
        conditions: data.conditions.slice(-n)
    };
}

// ─── Shorten date labels for axis ─────────────────────────────
function shortLabels(dates) {
    return dates.map(d => {
        const dt = new Date(d);
        return dt.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
    });
}

// ─── Fetch & render all charts ────────────────────────────────
let rawData = null;

async function fetchAndRender(days = 90) {
    if (!rawData) {
        try {
            const resp = await fetch('/api/chart-data');
            if (!resp.ok) throw new Error('API error');
            rawData = await resp.json();
        } catch (err) {
            console.error('Chart data error:', err);
            document.querySelectorAll('.chart-wrapper canvas').forEach(c => {
                c.parentElement.innerHTML =
                    '<div class="chart-placeholder">⚠️ Could not load data. Run training first.</div>';
            });
            return;
        }
    }

    const d = sliceData(rawData, days);
    const labels = shortLabels(d.dates);

    updateMetrics(d);
    renderTempChart(labels, d.temperature);
    renderRainfallChart(labels, d.rainfall);
    renderHumidityChart(labels, d.humidity);
    renderPressureChart(labels, d.pressure);
    renderConditionChart();
}

// ─── Init ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Mobile nav
    const toggle = document.getElementById('navToggle');
    const navLinks = document.querySelector('.nav-links');
    if (toggle && navLinks) {
        toggle.addEventListener('click', () => {
            navLinks.classList.toggle('open');
            toggle.textContent = navLinks.classList.contains('open') ? '✕' : '☰';
        });
    }

    // Time range selector
    const rangeSelect = document.getElementById('time-range');
    rangeSelect?.addEventListener('change', () => {
        fetchAndRender(parseInt(rangeSelect.value));
    });

    fetchAndRender(90);
});
