/**
 * predict.js  –  Prediction page logic
 * Handles: form validation, API fetch, result display, history, CSV download
 */

// ─── Prediction presets ───────────────────────────────────────
const PRESETS = {
    sunny: { humidity: 38, wind_speed: 12, pressure: 1020, prev_temperature: 32 },
    rainy: { humidity: 88, wind_speed: 25, pressure: 998, prev_temperature: 18 },
    cloudy: { humidity: 70, wind_speed: 17, pressure: 1007, prev_temperature: 22 },
    storm: { humidity: 95, wind_speed: 55, pressure: 985, prev_temperature: 15 }
};

// ─── Condition icons & advice ─────────────────────────────────
const CONDITION_ICONS = {
    'Sunny': '☀️',
    'Partly Cloudy': '⛅',
    'Cloudy': '☁️',
    'Rainy': '🌧️',
    'Drizzle': '🌦️',
    'default': '🌤️'
};

const CONDITION_ADVICE = {
    'Sunny':
        '☀️ Great day! Wear sunscreen and stay hydrated. UV levels may be high during midday hours.',
    'Partly Cloudy':
        '⛅ Pleasant conditions expected. Good day for outdoor activities with occasional shade.',
    'Cloudy':
        '☁️ Overcast skies. Carry a light jacket as temperatures may feel cooler than expected.',
    'Rainy':
        '🌧️ Bring an umbrella! Avoid driving in low visibility and watch for puddles and slippery roads.',
    'Drizzle':
        '🌦️ Light drizzle expected. A waterproof jacket should suffice for outdoor activities.',
    'default':
        '🌈 Variable conditions. Check local advisories for more specific guidance.'
};

// ─── State ────────────────────────────────────────────────────
let predictionHistory = [];

// ─── DOM helpers ─────────────────────────────────────────────
const $ = id => document.getElementById(id);

function setVal(id, val) {
    const el = $(id);
    if (el) el.textContent = val;
}

// ─── Rangebar update ──────────────────────────────────────────
function updateRangebar(inputId, fillId, min, max) {
    const input = $(inputId);
    const fill = $(fillId);
    if (!input || !fill) return;

    const update = () => {
        const pct = Math.min(100, Math.max(0,
            ((parseFloat(input.value) - min) / (max - min)) * 100
        ));
        fill.style.width = pct + '%';
    };
    input.addEventListener('input', update);
    input.addEventListener('change', update);
    update();
}

// ─── Form validation ─────────────────────────────────────────
function validateForm() {
    const fields = [
        { id: 'humidity', errId: 'err-humidity', min: 0, max: 100, label: 'Humidity' },
        { id: 'wind_speed', errId: 'err-wind', min: 0, max: 150, label: 'Wind Speed' },
        { id: 'pressure', errId: 'err-pressure', min: 940, max: 1060, label: 'Pressure' },
        { id: 'prev_temperature', errId: 'err-prev-temp', min: -30, max: 55, label: 'Prev Temperature' }
    ];

    let valid = true;
    fields.forEach(({ id, errId, min, max, label }) => {
        const input = $(id);
        const err = $(errId);
        const val = parseFloat(input.value);
        if (!input.value || isNaN(val) || val < min || val > max) {
            err.textContent = `${label} must be between ${min} and ${max}`;
            err.classList.add('visible');
            input.style.borderColor = 'var(--clr-red)';
            valid = false;
        } else {
            err.classList.remove('visible');
            input.style.borderColor = '';
        }
    });
    return valid;
}

// ─── Show result ──────────────────────────────────────────────
function showResult(data) {
    $('result-placeholder').style.display = 'none';
    const card = $('result-card');
    card.style.display = 'block';

    const icon = CONDITION_ICONS[data.predicted_condition] || CONDITION_ICONS.default;
    $('result-icon').textContent = icon;
    $('result-condition').textContent = data.predicted_condition || '--';
    $('result-temp-val').textContent =
        data.predicted_temperature != null ? data.predicted_temperature : '--';

    // Details
    setVal('det-feels', data.feels_like != null ? `${data.feels_like}°C` : '--');
    setVal('det-rain', data.rain_chance != null ? `${data.rain_chance}%` : '--');
    setVal('det-conf', data.confidence != null ? `${data.confidence}%` : 'N/A');
    setVal('det-hum', data.inputs?.humidity != null ? `${data.inputs.humidity}%` : '--');
    setVal('det-pres', data.inputs?.pressure != null ? `${data.inputs.pressure} hPa` : '--');
    setVal('det-wind', data.inputs?.wind_speed != null ? `${data.inputs.wind_speed} km/h` : '--');

    // Rain bar
    const rainPct = Math.min(100, Math.max(0, data.rain_chance || 0));
    $('rain-bar-fill').style.width = rainPct + '%';
    $('rain-pct-label').textContent = `${rainPct.toFixed(1)}%`;

    // Advice
    const advice = CONDITION_ADVICE[data.predicted_condition] || CONDITION_ADVICE.default;
    $('condition-advice').textContent = advice;

    // Timestamp
    const ts = new Date().toLocaleString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
    $('result-timestamp').textContent = `Prediction at ${ts}`;

    // Scroll to result on mobile
    if (window.innerWidth < 900) {
        card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Add to history
    addToHistory({
        timestamp: ts,
        humidity: data.inputs?.humidity,
        wind_speed: data.inputs?.wind_speed,
        pressure: data.inputs?.pressure,
        prev_temperature: data.inputs?.prev_temperature,
        predicted_temperature: data.predicted_temperature,
        predicted_condition: data.predicted_condition,
        feels_like: data.feels_like,
        rain_chance: data.rain_chance
    });
}

// ─── History panel ────────────────────────────────────────────
function addToHistory(entry) {
    predictionHistory.unshift(entry);
    if (predictionHistory.length > 20) predictionHistory.pop();

    const panel = $('history-panel');
    const list = $('history-list');
    panel.style.display = 'block';

    const icon = CONDITION_ICONS[entry.predicted_condition] || '🌤️';
    const item = document.createElement('div');
    item.className = 'history-item';
    item.innerHTML = `
    <span>${icon}</span>
    <span class="hi-temp">${entry.predicted_temperature}°C</span>
    <span class="hi-cond">${entry.predicted_condition}</span>
    <span class="hi-time">${entry.timestamp}</span>
  `;
    list.insertBefore(item, list.firstChild);
}

// ─── CSV Download ─────────────────────────────────────────────
async function downloadCSV() {
    if (!predictionHistory.length) return;

    try {
        const resp = await fetch('/api/download-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ predictions: predictionHistory })
        });

        if (!resp.ok) throw new Error('Download failed');

        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `weather_predictions_${Date.now()}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (err) {
        console.error('CSV download error:', err);
        alert('Failed to download CSV. Please try again.');
    }
}

// ─── Set current month in select ─────────────────────────────
function setCurrentMonth() {
    const monthSelect = $('month');
    if (monthSelect) {
        monthSelect.value = new Date().getMonth() + 1;
    }
}

// ─── Main form submit ─────────────────────────────────────────
async function handleSubmit(e) {
    e.preventDefault();
    if (!validateForm()) return;

    const btn = $('predict-btn');
    const spinner = $('btn-spinner');
    const btnText = $('btn-text');

    // Loading state
    btn.disabled = true;
    spinner.style.display = 'inline';
    btnText.textContent = 'Predicting…';

    const payload = {
        humidity: parseFloat($('humidity').value),
        wind_speed: parseFloat($('wind_speed').value),
        pressure: parseFloat($('pressure').value),
        prev_temperature: parseFloat($('prev_temperature').value),
        month: parseInt($('month').value),
        day_of_year: Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0)) / 86400000)
    };

    try {
        const resp = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await resp.json();

        if (!resp.ok || data.error) {
            throw new Error(data.error || 'Server error');
        }

        showResult(data);

    } catch (err) {
        console.error('Prediction error:', err);
        alert(`Prediction failed: ${err.message}\n\nMake sure the ML models are trained by running: python train_models.py`);
    } finally {
        btn.disabled = false;
        spinner.style.display = 'none';
        btnText.textContent = '🔮 Generate Forecast';
    }
}

// ─── Presets ─────────────────────────────────────────────────
function initPresets() {
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const preset = btn.dataset.preset;
            const data = PRESETS[preset];
            if (!data) return;

            // Fill in values
            Object.entries(data).forEach(([key, val]) => {
                const input = $(key);
                if (input) {
                    input.value = val;
                    input.dispatchEvent(new Event('input'));
                }
            });

            // Highlight active preset
            document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
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

    setCurrentMonth();
    initPresets();
    updateRangebar('humidity', 'humidity-fill', 0, 100);
    updateRangebar('wind_speed', 'wind-fill', 0, 100);

    $('predict-form')?.addEventListener('submit', handleSubmit);
    $('download-csv-btn')?.addEventListener('click', downloadCSV);

    // Clear validation on input
    ['humidity', 'wind_speed', 'pressure', 'prev_temperature'].forEach(id => {
        const el = $(id);
        if (el) {
            el.addEventListener('input', () => { el.style.borderColor = ''; });
        }
    });
});
