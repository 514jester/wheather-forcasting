"""
generate_dataset.py
Generates a realistic synthetic weather dataset for demonstration.
Simulates seasonal trends, correlations between features, and realistic distributions.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)

def generate_weather_dataset(n_days=1825):  # 5 years of data
    """Generate a realistic weather dataset with seasonal patterns."""
    
    start_date = datetime(2019, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_days)]
    
    records = []
    for i, date in enumerate(dates):
        # Day of year (0-365) for seasonal calculation
        day_of_year = date.timetuple().tm_yday
        
        # Seasonal temperature pattern (sine wave)
        # Peak in summer (~day 182), trough in winter (~day 0/365)
        seasonal_temp = 22 + 14 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        # Add daily noise
        temperature = seasonal_temp + np.random.normal(0, 3.5)
        temperature = round(max(-5, min(45, temperature)), 1)
        
        # Humidity inversely related to temperature (with noise)
        base_humidity = 75 - 0.8 * (temperature - 22) + np.random.normal(0, 10)
        humidity = round(max(20, min(100, base_humidity)), 1)
        
        # Wind speed - higher in winter/spring
        wind_seasonal = 18 - 8 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        wind_speed = round(max(0, wind_seasonal + np.random.exponential(5)), 1)
        wind_speed = min(wind_speed, 80)
        
        # Pressure - inversely related to humidity/rain probability
        pressure_base = 1013 + np.random.normal(0, 8)
        pressure = round(max(970, min(1040, pressure_base - 0.05 * humidity + np.random.normal(0, 3))), 1)
        
        # Rainfall probability based on humidity and pressure
        rain_prob = max(0, (humidity - 55) / 100 + (1010 - pressure) / 200)
        rain_prob = min(1, rain_prob + np.random.normal(0, 0.05))
        
        if rain_prob > 0.55:
            rainfall = round(np.random.exponential(8) + 1, 1)
            rainfall = min(rainfall, 80)
        else:
            rainfall = round(max(0, np.random.exponential(0.5)), 1)
        
        # Weather condition based on features
        if rainfall > 5:
            condition = "Rainy"
        elif rainfall > 0 and humidity > 70:
            condition = "Drizzle"
        elif humidity > 80 and pressure < 1008:
            condition = "Cloudy"
        elif humidity > 70 and pressure < 1015:
            condition = np.random.choice(["Cloudy", "Partly Cloudy"], p=[0.6, 0.4])
        elif temperature > 30 and humidity < 50:
            condition = "Sunny"
        elif temperature > 25 and humidity < 65:
            condition = np.random.choice(["Sunny", "Partly Cloudy"], p=[0.7, 0.3])
        else:
            condition = np.random.choice(["Partly Cloudy", "Sunny", "Cloudy"], p=[0.4, 0.35, 0.25])
        
        # Randomly introduce missing values (~2%)
        if np.random.random() < 0.02:
            missing_col = np.random.choice(['Humidity (%)', 'Wind Speed (km/h)', 'Pressure (hPa)'])
        
        records.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Temperature (C)': temperature,
            'Humidity (%)': humidity,
            'Wind Speed (km/h)': wind_speed,
            'Pressure (hPa)': pressure,
            'Rainfall (mm)': rainfall,
            'Weather Condition': condition
        })
    
    df = pd.DataFrame(records)
    
    # Introduce some missing values realistically
    for col in ['Humidity (%)', 'Wind Speed (km/h)', 'Pressure (hPa)', 'Rainfall (mm)']:
        mask = np.random.random(len(df)) < 0.015
        df.loc[mask, col] = np.nan
    
    return df


if __name__ == "__main__":
    print("Generating weather dataset...")
    df = generate_weather_dataset(1825)
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/weather_data.csv', index=False)
    
    print(f"Dataset generated: {len(df)} records")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"\nDataset summary:")
    print(df.describe())
    print(f"\nWeather conditions distribution:")
    print(df['Weather Condition'].value_counts())
    print(f"\nMissing values:")
    print(df.isnull().sum())
    print(f"\nDataset saved to: data/weather_data.csv")
