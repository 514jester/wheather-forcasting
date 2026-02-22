"""
train_models.py
ML pipeline for Weather Forecasting System.
Trains:
  - Linear Regression for temperature prediction
  - Random Forest Classifier for weather condition prediction
Saves models, metrics, and preprocessors to disk.
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, classification_report, confusion_matrix
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns


# ─────────────────────────────────────────────
# 1. LOAD & PREPROCESS DATA
# ─────────────────────────────────────────────
def load_and_preprocess(filepath='data/weather_data.csv'):
    print("=" * 60)
    print("  WEATHER FORECASTING MODEL TRAINING PIPELINE")
    print("=" * 60)
    
    df = pd.read_csv(filepath)
    print(f"\n[1] Dataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")
    
    # ── Parse dates & extract features
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    df['DayOfYear'] = df['Date'].dt.dayofyear
    df['Season'] = df['Month'].map({
        12: 0, 1: 0, 2: 0,   # Winter
        3: 1, 4: 1, 5: 1,    # Spring
        6: 2, 7: 2, 8: 2,    # Summer
        9: 3, 10: 3, 11: 3   # Autumn
    })
    
    # ── Handle missing values
    numeric_cols = ['Temperature (C)', 'Humidity (%)', 'Wind Speed (km/h)',
                    'Pressure (hPa)', 'Rainfall (mm)']
    missing_before = df[numeric_cols].isnull().sum().sum()
    
    for col in numeric_cols:
        df[col].fillna(df[col].median(), inplace=True)
    
    print(f"[2] Handled {missing_before} missing values (filled with median)")
    
    # ── Encode weather condition
    le = LabelEncoder()
    df['Condition_Encoded'] = le.fit_transform(df['Weather Condition'])
    
    print(f"[3] Encoded weather conditions: {list(le.classes_)}")
    
    return df, le


# ─────────────────────────────────────────────
# 2. TRAIN TEMPERATURE REGRESSION MODELS
# ─────────────────────────────────────────────
def train_regression_models(df):
    print("\n" + "─" * 60)
    print("  TEMPERATURE PREDICTION (REGRESSION)")
    print("─" * 60)
    
    features = ['Humidity (%)', 'Wind Speed (km/h)', 'Pressure (hPa)',
                 'Rainfall (mm)', 'Month', 'DayOfYear', 'Season']
    target = 'Temperature (C)'
    
    X = df[features].values
    y = df[target].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    
    # ── Model A: Linear Regression
    lr_model = LinearRegression()
    lr_model.fit(X_train_s, y_train)
    lr_pred = lr_model.predict(X_test_s)
    
    lr_metrics = {
        'MAE': round(mean_absolute_error(y_test, lr_pred), 4),
        'RMSE': round(np.sqrt(mean_squared_error(y_test, lr_pred)), 4),
        'R2': round(r2_score(y_test, lr_pred), 4)
    }
    print(f"\n  Linear Regression:")
    print(f"    MAE  = {lr_metrics['MAE']} °C")
    print(f"    RMSE = {lr_metrics['RMSE']} °C")
    print(f"    R²   = {lr_metrics['R2']}")
    
    # ── Model B: Random Forest Regressor
    rf_reg = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf_reg.fit(X_train_s, y_train)
    rf_pred = rf_reg.predict(X_test_s)
    
    rf_metrics = {
        'MAE': round(mean_absolute_error(y_test, rf_pred), 4),
        'RMSE': round(np.sqrt(mean_squared_error(y_test, rf_pred)), 4),
        'R2': round(r2_score(y_test, rf_pred), 4)
    }
    print(f"\n  Random Forest Regressor:")
    print(f"    MAE  = {rf_metrics['MAE']} °C")
    print(f"    RMSE = {rf_metrics['RMSE']} °C")
    print(f"    R²   = {rf_metrics['R2']}")
    
    # ── Select best regression model
    best_reg = 'Random Forest' if rf_metrics['R2'] > lr_metrics['R2'] else 'Linear Regression'
    best_reg_model = rf_reg if best_reg == 'Random Forest' else lr_model
    best_reg_metrics = rf_metrics if best_reg == 'Random Forest' else lr_metrics
    print(f"\n  ★ Best Regression Model: {best_reg} (R² = {best_reg_metrics['R2']})")
    
    return {
        'best_model': best_reg_model,
        'best_name': best_reg,
        'scaler': scaler,
        'features': features,
        'lr_metrics': lr_metrics,
        'rf_metrics': rf_metrics,
        'best_metrics': best_reg_metrics,
        'y_test': y_test.tolist(),
        'best_pred': (rf_pred if best_reg == 'Random Forest' else lr_pred).tolist()
    }


# ─────────────────────────────────────────────
# 3. TRAIN WEATHER CONDITION CLASSIFIERS
# ─────────────────────────────────────────────
def train_classification_models(df, le):
    print("\n" + "─" * 60)
    print("  WEATHER CONDITION PREDICTION (CLASSIFICATION)")
    print("─" * 60)
    
    features = ['Temperature (C)', 'Humidity (%)', 'Wind Speed (km/h)',
                 'Pressure (hPa)', 'Rainfall (mm)', 'Month', 'Season']
    target = 'Condition_Encoded'
    
    X = df[features].values
    y = df[target].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    
    # ── Model A: Decision Tree
    dt_model = DecisionTreeClassifier(max_depth=10, min_samples_split=10, random_state=42)
    dt_model.fit(X_train_s, y_train)
    dt_pred = dt_model.predict(X_test_s)
    dt_acc = round(accuracy_score(y_test, dt_pred) * 100, 2)
    print(f"\n  Decision Tree Classifier:")
    print(f"    Accuracy = {dt_acc}%")
    
    # ── Model B: Random Forest Classifier
    rf_model = RandomForestClassifier(n_estimators=150, max_depth=15, random_state=42, n_jobs=-1)
    rf_model.fit(X_train_s, y_train)
    rf_pred = rf_model.predict(X_test_s)
    rf_acc = round(accuracy_score(y_test, rf_pred) * 100, 2)
    print(f"\n  Random Forest Classifier:")
    print(f"    Accuracy = {rf_acc}%")
    
    # ── Select best classifier
    best_clf = 'Random Forest' if rf_acc > dt_acc else 'Decision Tree'
    best_clf_model = rf_model if best_clf == 'Random Forest' else dt_model
    best_pred = rf_pred if best_clf == 'Random Forest' else dt_pred
    best_acc = rf_acc if best_clf == 'Random Forest' else dt_acc
    
    print(f"\n  ★ Best Classifier: {best_clf} (Accuracy = {best_acc}%)")
    
    # Classification report
    report = classification_report(y_test, best_pred,
                                    target_names=le.classes_, output_dict=True)
    
    # Confusion matrix data
    cm = confusion_matrix(y_test, best_pred)
    
    return {
        'best_model': best_clf_model,
        'best_name': best_clf,
        'scaler': scaler,
        'features': features,
        'dt_accuracy': dt_acc,
        'rf_accuracy': rf_acc,
        'best_accuracy': best_acc,
        'confusion_matrix': cm.tolist(),
        'classification_report': report,
        'y_test': y_test.tolist(),
        'best_pred': best_pred.tolist(),
        'classes': le.classes_.tolist()
    }


# ─────────────────────────────────────────────
# 4. GENERATE CHARTS
# ─────────────────────────────────────────────
def generate_charts(df, reg_results, clf_results):
    print("\n" + "─" * 60)
    print("  GENERATING CHARTS")
    print("─" * 60)
    
    os.makedirs('static/charts', exist_ok=True)
    
    # Style
    plt.rcParams.update({
        'figure.facecolor': '#0f172a',
        'axes.facecolor': '#1e293b',
        'axes.edgecolor': '#334155',
        'axes.labelcolor': '#94a3b8',
        'xtick.color': '#64748b',
        'ytick.color': '#64748b',
        'text.color': '#e2e8f0',
        'grid.color': '#1e293b',
        'grid.alpha': 0.3,
        'font.family': 'DejaVu Sans'
    })
    
    # ── Chart 1: Temperature Over Time
    sample_df = df.tail(365).copy()
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(pd.to_datetime(sample_df['Date']),
             sample_df['Temperature (C)'],
             color='#f97316', linewidth=1.5, alpha=0.9)
    ax.fill_between(pd.to_datetime(sample_df['Date']),
                     sample_df['Temperature (C)'],
                     alpha=0.15, color='#f97316')
    ax.set_title('Temperature Trend (Last 12 Months)', fontsize=14,
                   color='#f1f5f9', fontweight='bold', pad=12)
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylabel('Temperature (°C)', fontsize=10)
    ax.grid(True, alpha=0.2, color='#475569')
    plt.tight_layout()
    plt.savefig('static/charts/temperature_trend.png', dpi=120,
                 bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    print("  ✓ temperature_trend.png")
    
    # ── Chart 2: Monthly Rainfall
    df['Month_Name'] = pd.to_datetime(df['Date']).dt.strftime('%b')
    df['Month_Num'] = pd.to_datetime(df['Date']).dt.month
    monthly_rain = df.groupby('Month_Num')['Rainfall (mm)'].mean()
    month_names = ['Jan','Feb','Mar','Apr','May','Jun',
                    'Jul','Aug','Sep','Oct','Nov','Dec']
    colors = ['#3b82f6' if r < monthly_rain.mean() else '#0ea5e9'
               for r in monthly_rain.values]
    
    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.bar(month_names, monthly_rain.values, color=colors,
                   edgecolor='#1e40af', linewidth=0.5, width=0.7)
    ax.set_title('Average Monthly Rainfall', fontsize=14,
                   color='#f1f5f9', fontweight='bold', pad=12)
    ax.set_xlabel('Month', fontsize=10)
    ax.set_ylabel('Avg Rainfall (mm)', fontsize=10)
    ax.grid(True, alpha=0.2, axis='y', color='#475569')
    for bar, val in zip(bars, monthly_rain.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                 f'{val:.1f}', ha='center', va='bottom', fontsize=8, color='#cbd5e1')
    plt.tight_layout()
    plt.savefig('static/charts/rainfall_chart.png', dpi=120,
                 bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    print("  ✓ rainfall_chart.png")
    
    # ── Chart 3: Model Accuracy Comparison
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    
    # Regression: R² comparison
    reg_names = ['Linear\nRegression', 'Random\nForest']
    reg_r2 = [reg_results['lr_metrics']['R2'], reg_results['rf_metrics']['R2']]
    reg_colors = ['#a78bfa', '#818cf8']
    bars1 = axes[0].bar(reg_names, [v*100 for v in reg_r2],
                          color=reg_colors, edgecolor='#4c1d95', width=0.5)
    axes[0].set_title('Regression R² Score (%)', fontsize=12,
                        color='#f1f5f9', fontweight='bold')
    axes[0].set_ylim(0, 100)
    axes[0].set_ylabel('R² (%)', fontsize=10)
    axes[0].grid(True, alpha=0.2, axis='y', color='#475569')
    for bar, val in zip(bars1, reg_r2):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                      f'{val*100:.1f}%', ha='center', va='bottom',
                      fontsize=10, fontweight='bold', color='#e2e8f0')
    
    # Classification: Accuracy comparison
    clf_names = ['Decision\nTree', 'Random\nForest']
    clf_accs = [clf_results['dt_accuracy'], clf_results['rf_accuracy']]
    clf_colors = ['#34d399', '#10b981']
    bars2 = axes[1].bar(clf_names, clf_accs,
                          color=clf_colors, edgecolor='#064e3b', width=0.5)
    axes[1].set_title('Classifier Accuracy (%)', fontsize=12,
                        color='#f1f5f9', fontweight='bold')
    axes[1].set_ylim(0, 100)
    axes[1].set_ylabel('Accuracy (%)', fontsize=10)
    axes[1].grid(True, alpha=0.2, axis='y', color='#475569')
    for bar, val in zip(bars2, clf_accs):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                      f'{val:.1f}%', ha='center', va='bottom',
                      fontsize=10, fontweight='bold', color='#e2e8f0')
    
    plt.tight_layout(pad=2)
    plt.savefig('static/charts/model_accuracy.png', dpi=120,
                 bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    print("  ✓ model_accuracy.png")
    
    # ── Chart 4: Confusion Matrix
    cm = np.array(clf_results['confusion_matrix'])
    classes = clf_results['classes']
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, interpolation='nearest', cmap='Blues')
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title(f'Confusion Matrix\n({clf_results["best_name"]})',
                  fontsize=13, color='#f1f5f9', fontweight='bold')
    tick_marks = np.arange(len(classes))
    ax.set_xticks(tick_marks)
    ax.set_yticks(tick_marks)
    ax.set_xticklabels(classes, rotation=30, ha='right', fontsize=8)
    ax.set_yticklabels(classes, fontsize=8)
    thresh = cm.max() / 2
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]),
                     ha='center', va='center',
                     color='white' if cm[i, j] > thresh else '#1e293b',
                     fontsize=9)
    ax.set_ylabel('True Label', fontsize=10, color='#94a3b8')
    ax.set_xlabel('Predicted Label', fontsize=10, color='#94a3b8')
    plt.tight_layout()
    plt.savefig('static/charts/confusion_matrix.png', dpi=120,
                 bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    print("  ✓ confusion_matrix.png")
    
    # ── Chart 5: Weather Condition Distribution
    condition_counts = df['Weather Condition'].value_counts()
    colors_pie = ['#f97316', '#3b82f6', '#a78bfa', '#10b981', '#f59e0b', '#ef4444']
    fig, ax = plt.subplots(figsize=(7, 5))
    wedges, texts, autotexts = ax.pie(
        condition_counts.values,
        labels=condition_counts.index,
        colors=colors_pie[:len(condition_counts)],
        autopct='%1.1f%%',
        pctdistance=0.8,
        startangle=140,
        wedgeprops={'edgecolor': '#0f172a', 'linewidth': 2}
    )
    for text in texts:
        text.set_color('#cbd5e1')
        text.set_fontsize(9)
    for autotext in autotexts:
        autotext.set_color('#f1f5f9')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(8)
    ax.set_title('Weather Condition Distribution', fontsize=13,
                  color='#f1f5f9', fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig('static/charts/condition_distribution.png', dpi=120,
                 bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    print("  ✓ condition_distribution.png")


# ─────────────────────────────────────────────
# 5. SAVE MODELS & METRICS
# ─────────────────────────────────────────────
def save_artifacts(reg_results, clf_results, le, df):
    os.makedirs('models', exist_ok=True)
    
    # Save regression model + scaler
    with open('models/regression_model.pkl', 'wb') as f:
        pickle.dump(reg_results['best_model'], f)
    with open('models/regression_scaler.pkl', 'wb') as f:
        pickle.dump(reg_results['scaler'], f)
    
    # Save classification model + scaler
    with open('models/classifier_model.pkl', 'wb') as f:
        pickle.dump(clf_results['best_model'], f)
    with open('models/classifier_scaler.pkl', 'wb') as f:
        pickle.dump(clf_results['scaler'], f)
    
    # Save label encoder
    with open('models/label_encoder.pkl', 'wb') as f:
        pickle.dump(le, f)
    
    # Save metrics to JSON (used by Flask)
    metrics = {
        'regression': {
            'best_model': reg_results['best_name'],
            'features': reg_results['features'],
            'linear_regression': reg_results['lr_metrics'],
            'random_forest': reg_results['rf_metrics'],
            'best_metrics': reg_results['best_metrics']
        },
        'classification': {
            'best_model': clf_results['best_name'],
            'features': clf_results['features'],
            'decision_tree_accuracy': clf_results['dt_accuracy'],
            'random_forest_accuracy': clf_results['rf_accuracy'],
            'best_accuracy': clf_results['best_accuracy'],
            'confusion_matrix': clf_results['confusion_matrix'],
            'classes': clf_results['classes'],
            'classification_report': clf_results['classification_report']
        },
        'dataset': {
            'total_records': len(df),
            'date_range': f"{df['Date'].min()} to {df['Date'].max()}",
            'features': ['Temperature (C)', 'Humidity (%)', 'Wind Speed (km/h)',
                          'Pressure (hPa)', 'Rainfall (mm)', 'Weather Condition']
        }
    }
    
    with open('models/metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    # Save recent data for visualization
    recent_df = df.tail(365)[['Date', 'Temperature (C)', 'Humidity (%)',
                                'Wind Speed (km/h)', 'Pressure (hPa)',
                                'Rainfall (mm)', 'Weather Condition']].copy()
    recent_df.to_csv('data/recent_data.csv', index=False)
    
    print("\n  Saved artifacts:")
    print("  ✓ models/regression_model.pkl")
    print("  ✓ models/regression_scaler.pkl")
    print("  ✓ models/classifier_model.pkl")
    print("  ✓ models/classifier_scaler.pkl")
    print("  ✓ models/label_encoder.pkl")
    print("  ✓ models/metrics.json")
    print("  ✓ data/recent_data.csv")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == '__main__':
    df, le = load_and_preprocess('data/weather_data.csv')
    
    reg_results = train_regression_models(df)
    clf_results = train_classification_models(df, le)
    
    generate_charts(df, reg_results, clf_results)
    save_artifacts(reg_results, clf_results, le, df)
    
    print("\n" + "=" * 60)
    print("  TRAINING COMPLETE ✓")
    print(f"  Best Regressor  : {reg_results['best_name']}")
    print(f"  Best Classifier : {clf_results['best_name']}")
    print(f"  Regression R²   : {reg_results['best_metrics']['R2']}")
    print(f"  Classifier Acc  : {clf_results['best_accuracy']}%")
    print("=" * 60)
