"""
app.py
Flask backend for the Weather Forecasting Web Application.
Serves all pages and provides REST API endpoints for predictions.
"""

from flask import Flask, render_template, request, jsonify, send_file
import pickle
import json
import numpy as np
import pandas as pd
import io
import csv
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# ─────────────────────────────────────────────
# Load models & artifacts at startup
# ─────────────────────────────────────────────
def load_models():
    """Load all trained models and artifacts."""
    models = {}
    try:
        with open('models/regression_model.pkl', 'rb') as f:
            models['reg_model'] = pickle.load(f)
        with open('models/regression_scaler.pkl', 'rb') as f:
            models['reg_scaler'] = pickle.load(f)
        with open('models/classifier_model.pkl', 'rb') as f:
            models['clf_model'] = pickle.load(f)
        with open('models/classifier_scaler.pkl', 'rb') as f:
            models['clf_scaler'] = pickle.load(f)
        with open('models/label_encoder.pkl', 'rb') as f:
            models['label_encoder'] = pickle.load(f)
        with open('models/metrics.json', 'r') as f:
            models['metrics'] = json.load(f)
        print("[OK] All models loaded successfully.")
    except FileNotFoundError as e:
        print(f"[WARN] Model file not found: {e}")
        print("[INFO] Please run: python generate_dataset.py && python train_models.py")
    return models

MODELS = load_models()


def load_recent_data():
    """Load recent weather data for visualizations."""
    try:
        df = pd.read_csv('data/recent_data.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except FileNotFoundError:
        return None


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route('/')
def home():
    """Home / landing page."""
    metrics = MODELS.get('metrics', {})
    return render_template('index.html', metrics=metrics)


@app.route('/predict')
def predict_page():
    """Prediction input page."""
    return render_template('predict.html')


@app.route('/dashboard')
def dashboard():
    """Data visualization dashboard."""
    return render_template('dashboard.html')


@app.route('/about')
def about():
    """About / model details page."""
    metrics = MODELS.get('metrics', {})
    return render_template('about.html', metrics=metrics)


# ─────────────────────────────────────────────
# API ENDPOINTS
# ─────────────────────────────────────────────

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    POST /api/predict
    Body (JSON): { humidity, wind_speed, pressure, prev_temperature, month (optional) }
    Returns: { predicted_temperature, predicted_condition, confidence }
    """
    try:
        data = request.get_json()

        # Validate required inputs
        required = ['humidity', 'wind_speed', 'pressure', 'prev_temperature']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        humidity = float(data['humidity'])
        wind_speed = float(data['wind_speed'])
        pressure = float(data['pressure'])
        prev_temp = float(data['prev_temperature'])
        month = int(data.get('month', datetime.now().month))

        # Derived features
        day_of_year = int(data.get('day_of_year', datetime.now().timetuple().tm_yday))
        season = {12: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1,
                   6: 2, 7: 2, 8: 2, 9: 3, 10: 3, 11: 3}[month]

        # ── Temperature Prediction
        # Features for regression: Humidity, Wind Speed, Pressure, Rainfall, Month, DayOfYear, Season
        # We estimate rainfall from inputs
        estimated_rainfall = max(0, (humidity - 60) * 0.3) if humidity > 60 else 0

        reg_features = np.array([[humidity, wind_speed, pressure,
                                    estimated_rainfall, month, day_of_year, season]])
        reg_features_scaled = MODELS['reg_scaler'].transform(reg_features)
        predicted_temp = float(MODELS['reg_model'].predict(reg_features_scaled)[0])
        
        # Blend with prev_temperature for realistic short-term prediction
        predicted_temp = round(0.65 * predicted_temp + 0.35 * prev_temp, 1)

        # ── Condition Prediction
        # Features: Temperature, Humidity, Wind Speed, Pressure, Rainfall, Month, Season
        clf_features = np.array([[predicted_temp, humidity, wind_speed,
                                    pressure, estimated_rainfall, month, season]])
        clf_features_scaled = MODELS['clf_scaler'].transform(clf_features)
        
        condition_idx = MODELS['clf_model'].predict(clf_features_scaled)[0]
        condition = MODELS['label_encoder'].inverse_transform([condition_idx])[0]
        
        # Get probability / confidence
        if hasattr(MODELS['clf_model'], 'predict_proba'):
            proba = MODELS['clf_model'].predict_proba(clf_features_scaled)[0]
            confidence = round(float(max(proba)) * 100, 1)
        else:
            confidence = None

        # Derive extras
        feels_like = round(predicted_temp - 0.4 * (humidity / 100) * (predicted_temp - 10), 1)
        rain_chance = round(min(100, max(0, (humidity - 50) * 2 + (1010 - pressure) * 0.5 +
                                          estimated_rainfall * 3)), 1)
        
        return jsonify({
            'predicted_temperature': predicted_temp,
            'predicted_condition': condition,
            'feels_like': feels_like,
            'rain_chance': rain_chance,
            'confidence': confidence,
            'inputs': {
                'humidity': humidity,
                'wind_speed': wind_speed,
                'pressure': pressure,
                'prev_temperature': prev_temp,
                'month': month
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chart-data')
def api_chart_data():
    """
    GET /api/chart-data
    Returns recent weather time-series data for charts.
    """
    df = load_recent_data()
    if df is None:
        return jsonify({'error': 'Data not available'}), 404

    # Sample to 90 days for cleaner charts
    sample = df.tail(90)

    return jsonify({
        'dates': sample['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'temperature': sample['Temperature (C)'].round(1).tolist(),
        'humidity': sample['Humidity (%)'].round(1).tolist(),
        'rainfall': sample['Rainfall (mm)'].round(1).tolist(),
        'pressure': sample['Pressure (hPa)'].round(1).tolist(),
        'conditions': sample['Weather Condition'].tolist()
    })


@app.route('/api/metrics')
def api_metrics():
    """GET /api/metrics - Returns model performance metrics."""
    metrics = MODELS.get('metrics', {})
    return jsonify(metrics)


@app.route('/api/condition-stats')
def api_condition_stats():
    """GET /api/condition-stats - Weather condition distribution."""
    df = load_recent_data()
    if df is None:
        return jsonify({'error': 'Data not available'}), 404
    
    counts = df['Weather Condition'].value_counts().to_dict()
    return jsonify(counts)


@app.route('/api/download-report', methods=['POST'])
def download_report():
    """
    POST /api/download-report
    Downloads prediction results as CSV.
    """
    try:
        data = request.get_json()
        predictions = data.get('predictions', [])

        if not predictions:
            return jsonify({'error': 'No predictions to download'}), 400

        output = io.StringIO()
        fieldnames = ['Timestamp', 'Humidity (%)', 'Wind Speed (km/h)',
                       'Pressure (hPa)', 'Prev Temperature (°C)',
                       'Predicted Temperature (°C)', 'Predicted Condition',
                       'Feels Like (°C)', 'Rain Chance (%)']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for p in predictions:
            writer.writerow({
                'Timestamp': p.get('timestamp', ''),
                'Humidity (%)': p.get('humidity', ''),
                'Wind Speed (km/h)': p.get('wind_speed', ''),
                'Pressure (hPa)': p.get('pressure', ''),
                'Prev Temperature (°C)': p.get('prev_temperature', ''),
                'Predicted Temperature (°C)': p.get('predicted_temperature', ''),
                'Predicted Condition': p.get('predicted_condition', ''),
                'Feels Like (°C)': p.get('feels_like', ''),
                'Rain Chance (%)': p.get('rain_chance', '')
            })

        output.seek(0)
        byte_output = io.BytesIO(output.getvalue().encode('utf-8'))
        byte_output.seek(0)

        return send_file(
            byte_output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'weather_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Weather Forecasting System")
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
