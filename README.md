# WeatherPredict 🌦️

A Django-based weather forecasting web app that combines procedurally generated weather data with a genuine machine learning prediction pipeline.

## Overview

WeatherPredict simulates realistic weather patterns for cities (with a focus on Bangladeshi cities) and uses a trained ML model to forecast temperatures for the upcoming days — all without relying on any external weather API.

## How It Works

### 1. Weather Data Generation (`forecast/services.py`)
- `get_weather_data()` generates weather data using a deterministic seed based on **city name + date**, so the same city and date always produce the same output.
- Temperatures are derived from a seasonal base (winter/summer/etc.), country average, and latitude factor — producing realistic values (roughly 15–30°C for BD cities).
- This data is **synthetic**, not pulled from any real-world source, but it is algorithmically consistent.

### 2. Machine Learning Model (`forecast/ml_service.py`)
- Uses a real **scikit-learn Polynomial Regression** pipeline (`PolynomialFeatures` + `LinearRegression`).
- `train_temperature_model()` trains the model on 90 days of simulated historical data.
- Features used: day of year, humidity, pressure, wind speed, and season (numerically encoded).
- `predict_multi_day()` generates a 7-day forecast.
- The **model and training logic are genuine ML**, but the training data is simulated rather than sourced from real historical weather records.

> **Note:** No external weather API is used. All weather data is procedurally generated using deterministic algorithms (seeded by city name and date) to produce realistic but synthetic weather patterns. The ML model is a genuine scikit-learn PolynomialFeatures + LinearRegression pipeline trained on this simulated historical data. To use real weather data, replace `get_weather_data()` with an actual API integration (e.g. OpenWeatherMap, WeatherAPI).

## Features
- City-based weather lookup (including default Bangladeshi cities)
- 7-day ML-based temperature forecast
- No API key required to run

## Tech Stack
- **Backend:** Django
- **ML:** scikit-learn (Polynomial Regression)
- **Frontend:** HTML, CSS, JavaScript

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Junaid706/weather-prediction-website.git
cd weather-prediction-website

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

The app will be available at `http://127.0.0.1:8000/`.

## Using Real Weather Data

To switch from synthetic data to real weather data, replace the logic inside `get_weather_data()` in `forecast/services.py` with a call to a real weather API (e.g. [OpenWeatherMap](https://openweathermap.org/api), [WeatherAPI](https://www.weatherapi.com/)). This will require an API key from the chosen provider.

## Project Structure

```
weather-prediction-website/
├── forecast/           # Core app: weather generation + ML logic
├── static/              # CSS, JS, images
├── templates/            # HTML templates
├── weather_site/          # Django project settings
├── manage.py
└── requirements.txt
```

## License

This project currently has no license specified.
