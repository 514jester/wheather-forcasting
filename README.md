# 🌤️ Weather Forecasting System

A machine learning-powered weather forecasting web application that predicts **temperature** and **weather conditions** using historical weather data.

---

## ✨ Features

- **Temperature Prediction** – Linear Regression & Random Forest Regressor
- **Condition Classification** – Decision Tree & Random Forest Classifier (Sunny / Cloudy / Rainy / Partly Cloudy / Drizzle)
- **Interactive Dashboard** – Line charts, bar charts, doughnut charts with Chart.js
- **Prediction History** – Download predictions as CSV report
- **Modern UI** – Dark glassmorphism design with animations

---

## 🗂️ Project Structure

```
weather-forecasting/
├── app.py                  ← Flask backend + REST API
├── generate_dataset.py     ← Generates 5-year synthetic weather dataset
├── train_models.py         ← ML training pipeline (preprocessing → training → evaluation)
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
│
├── data/
│   ├── weather_data.csv    ← Full training dataset (auto-generated)
│   └── recent_data.csv     ← Last 365 days for visualization
│
├── models/
│   ├── regression_model.pkl     ← Best regression model
│   ├── regression_scaler.pkl    ← Scaler for regression features
│   ├── classifier_model.pkl     ← Best classifier model
│   ├── classifier_scaler.pkl    ← Scaler for classification features
│   ├── label_encoder.pkl        ← LabelEncoder for weather conditions
│   └── metrics.json             ← All performance metrics (JSON)
│
├── static/
│   ├── css/style.css       ← Complete custom CSS (no framework)
│   ├── js/
│   │   ├── main.js         ← Shared utilities (stars, navbar, counters)
│   │   ├── predict.js      ← Prediction form logic + history + CSV
│   │   └── dashboard.js    ← Chart.js dashboard charts
│   └── charts/             ← Pre-generated PNG charts (from training)
│
└── templates/
    ├── index.html          ← Homepage
    ├── predict.html        ← Prediction page
    ├── dashboard.html      ← Analytics dashboard
    └── about.html          ← Model documentation
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Dataset

```bash
python generate_dataset.py
```
Creates `data/weather_data.csv` with 5 years of synthetic weather data.

### 3. Train ML Models

```bash
python train_models.py
```
This will:
- Preprocess data (handle missing values, encode, scale)
- Train Linear Regression + Random Forest Regressor
- Train Decision Tree + Random Forest Classifier
- Generate charts (PNG files in `static/charts/`)
- Save models to `models/` directory
- Print performance metrics

### 4. Run the Application

```bash
python app.py
```

Open your browser at: **http://127.0.0.1:5000**

---

## 🤖 Machine Learning Details

### Preprocessing Pipeline
| Step | Method |
|------|--------|
| Date parsing | Extract Month, Day, DayOfYear, Season |
| Missing values | Median imputation |
| Categorical encoding | `sklearn.LabelEncoder` |
| Feature scaling | `sklearn.StandardScaler` (z-score) |
| Train/test split | 80% / 20%, `random_state=42` |

### Regression Models (Temperature Prediction)
| Model | Features |
|-------|----------|
| Input features | Humidity, Wind Speed, Pressure, Rainfall, Month, DayOfYear, Season |
| Model A | `LinearRegression` |
| Model B | `RandomForestRegressor(n_estimators=100)` |
| Best model selected by | Highest R² score |

### Classification Models (Weather Condition)
| Model | Classes |
|-------|---------|
| Input features | Temperature, Humidity, Wind Speed, Pressure, Rainfall, Month, Season |
| Model A | `DecisionTreeClassifier(max_depth=10)` |
| Model B | `RandomForestClassifier(n_estimators=150)` |
| Classes | Sunny, Cloudy, Rainy, Partly Cloudy, Drizzle |
| Best model selected by | Highest accuracy |

### Evaluation Metrics
- **Regression**: MAE, RMSE, R² Score
- **Classification**: Accuracy, Confusion Matrix, Classification Report

---

## 🌐 API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Home page |
| GET | `/predict` | Prediction form page |
| GET | `/dashboard` | Analytics dashboard |
| GET | `/about` | Model documentation |
| POST | `/api/predict` | Get weather prediction |
| GET | `/api/chart-data` | Time-series data for charts |
| GET | `/api/metrics` | Model performance metrics |
| GET | `/api/condition-stats` | Weather condition distribution |
| POST | `/api/download-report` | Download predictions as CSV |

### POST `/api/predict` — Request Body

```json
{
  "humidity": 65,
  "wind_speed": 18,
  "pressure": 1013,
  "prev_temperature": 24,
  "month": 6
}
```

### Response

```json
{
  "predicted_temperature": 26.3,
  "predicted_condition": "Partly Cloudy",
  "feels_like": 25.1,
  "rain_chance": 22.4,
  "confidence": 87.5,
  "inputs": { ... }
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask 3.0 |
| ML | Scikit-learn (LinearRegression, RandomForest, DecisionTree) |
| Data | Pandas, NumPy |
| Charts (server) | Matplotlib, Seaborn |
| Charts (client) | Chart.js 4.4 |
| Frontend | HTML5, Vanilla CSS, Vanilla JS |
| Fonts | Google Fonts (Inter) |

---

## 📊 Dataset Schema

| Column | Type | Description |
|--------|------|-------------|
| Date | Date | YYYY-MM-DD format |
| Temperature (C) | Float | Air temperature in Celsius |
| Humidity (%) | Float | Relative humidity |
| Wind Speed (km/h) | Float | Wind speed |
| Pressure (hPa) | Float | Atmospheric pressure |
| Rainfall (mm) | Float | Daily rainfall |
| Weather Condition | String | Sunny/Cloudy/Rainy/Partly Cloudy/Drizzle |

The dataset is generated with realistic seasonal patterns:
- Temperature follows a sine wave (seasonal) with noise
- Humidity inversely correlates with temperature
- Rainfall probability based on humidity + low pressure
- ~1.5% missing values per column (healed during preprocessing)

---

## 📝 License

MIT License – feel free to use and modify for educational purposes.
