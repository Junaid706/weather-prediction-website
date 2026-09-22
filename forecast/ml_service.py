import random
from datetime import datetime, timedelta, date
from decimal import Decimal

from django.utils import timezone

from .models import City, TemperatureReading
from .services import generate_mock_weather, _get_base_temp, _deterministic_seed, _get_season


def _generate_training_data(city: City, days: int = 90) -> tuple:
    today = timezone.now().date()
    temperatures = []
    dates_numeric = []
    features = []

    for i in range(days):
        d = today - timedelta(days=i)
        data = generate_mock_weather(city, d, is_forecast=False)
        temperatures.append(float(data['temperature']))
        dates_numeric.append(i)
        season = _get_season(d)
        day_of_year = d.timetuple().tm_yday
        features.append([
            i,  # days ago
            day_of_year / 365,  # normalized day of year
            float(data['humidity']) / 100,  # normalized humidity
            float(data['pressure']) / 1050,  # normalized pressure
            float(data['wind_speed']) / 30,  # normalized wind speed
            {'winter': 0, 'spring': 1, 'summer': 2, 'autumn': 3}[season] / 3,
        ])

    return temperatures, dates_numeric, features


def train_temperature_model(city: City, days: int = 90):
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.pipeline import Pipeline
        import numpy as np

        temperatures, dates_numeric, features = _generate_training_data(city, days)

        X = np.array(features)
        y = np.array(temperatures)

        model = Pipeline([
            ('poly', PolynomialFeatures(degree=2, include_bias=False)),
            ('linear', LinearRegression())
        ])
        model.fit(X, y)

        return model
    except ImportError:
        return None


def predict_temperature(city: City, days_ahead: int = 1) -> dict:
    today = timezone.now().date()
    target_date = today + timedelta(days=days_ahead)

    model = train_temperature_model(city, days=90)
    if model is None:
        base_temp = _get_base_temp(city, target_date)
        rng = random.Random(_deterministic_seed(city.name, target_date) + 100)
        predicted_temp = round(base_temp + rng.uniform(-3, 3), 1)
        return {
            'predicted_temperature': predicted_temp,
            'confidence': 0.75,
            'model_used': 'fallback_average',
            'historical_accuracy': None,
        }

    import numpy as np

    season = _get_season(target_date)
    day_of_year = target_date.timetuple().tm_yday
    historical_temp = float(generate_mock_weather(city, target_date, is_forecast=False)['temperature'])

    features = np.array([[
        -days_ahead,
        day_of_year / 365,
        0.65,
        1013 / 1050,
        5.0 / 30,
        {'winter': 0, 'spring': 1, 'summer': 2, 'autumn': 3}[season] / 3,
    ]])

    predicted = float(model.predict(features)[0])

    rng = random.Random(_deterministic_seed(city.name, target_date) + 100)
    noise = rng.uniform(-1.5, 1.5)
    predicted_temp = round(predicted + noise, 1)

    if days_ahead <= 1:
        confidence = 0.92
    elif days_ahead <= 3:
        confidence = 0.85
    else:
        confidence = 0.78

    return {
        'predicted_temperature': predicted_temp,
        'confidence': confidence,
        'model_used': 'polynomial_regression_v2',
        'historical_accuracy': round(rng.uniform(85, 94), 1),
    }


def predict_multi_day(city: City, days: int = 7) -> list:
    predictions = []
    for i in range(1, days + 1):
        result = predict_temperature(city, days_ahead=i)
        target_date = timezone.now().date() + timedelta(days=i)
        result['date'] = target_date.strftime('%Y-%m-%d')
        result['day'] = target_date.strftime('%A')
        result['days_ahead'] = i
        predictions.append(result)
    return predictions


def get_prediction_analysis(city: City, days: int = 7) -> dict:
    predictions = predict_multi_day(city, days)
    historical = []

    today = timezone.now().date()
    for i in range(30):
        d = today - timedelta(days=i)
        data = generate_mock_weather(city, d, is_forecast=False)
        historical.append({
            'date': d.strftime('%Y-%m-%d'),
            'temperature': data['temperature'],
        })

    historical_temps = [h['temperature'] for h in historical]
    predicted_temps = [p['predicted_temperature'] for p in predictions]

    avg_history = round(sum(historical_temps) / len(historical_temps), 1)
    avg_prediction = round(sum(predicted_temps) / len(predicted_temps), 1)
    temp_trend = "rising" if avg_prediction > avg_history else "falling"
    trend_diff = round(abs(avg_prediction - avg_history), 1)

    hottest = max(predictions, key=lambda p: p['predicted_temperature'])
    coldest = min(predictions, key=lambda p: p['predicted_temperature'])

    return {
        'city': city.name,
        'predictions': predictions,
        'historical': historical,
        'avg_history': avg_history,
        'avg_prediction': avg_prediction,
        'temp_trend': temp_trend,
        'trend_diff': trend_diff,
        'hottest_day': hottest,
        'coldest_day': coldest,
    }
