import random
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from .models import City, WeatherData, TemperatureReading


WEATHER_CONDITIONS = [
    {'description': 'Clear sky', 'icon': '01d', 'color': '#0077ff'},
    {'description': 'Few clouds', 'icon': '02d', 'color': '#0099ff'},
    {'description': 'Scattered clouds', 'icon': '03d', 'color': '#00b3ff'},
    {'description': 'Broken clouds', 'icon': '04d', 'color': '#0099cc'},
    {'description': 'Shower rain', 'icon': '09d', 'color': '#4d94ff'},
    {'description': 'Rain', 'icon': '10d', 'color': '#0066cc'},
    {'description': 'Thunderstorm', 'icon': '11d', 'color': '#333399'},
    {'description': 'Mist', 'icon': '50d', 'color': '#cccccc'},
    {'description': 'Fog', 'icon': '50d', 'color': '#999999'},
    {'description': 'Dust', 'icon': '50d', 'color': '#c2b280'},
    {'description': 'Snow', 'icon': '13d', 'color': '#ffffff'},
    {'description': 'Light snow', 'icon': '13d', 'color': '#f0f0f0'},
]


SEASONAL_BASE_TEMPS = {
    'winter': {'min': -5, 'max': 10},
    'spring': {'min': 5, 'max': 22},
    'summer': {'min': 15, 'max': 38},
    'autumn': {'min': 3, 'max': 18},
}

BASE_TEMPS_BY_COUNTRY = {
    'US': 15,
    'CA': 5,
    'GB': 8,
    'IN': 25,
    'BR': 25,
    'AU': 18,
    'JP': 15,
    'CN': 18,
    'FR': 12,
    'DE': 10,
    'ES': 18,
    'IT': 16,
    'RU': 5,
    'ZA': 18,
    'MX': 22,
    'AR': 18,
    'KR': 14,
    'default': 15,
}

DEFAULT_CITIES = [
    ('New York', 'US', 40.71, -74.01, -5),
    ('London', 'GB', 51.51, -0.13, 0),
    ('Tokyo', 'JP', 35.68, 139.69, 9),
    ('Beijing', 'CN', 39.90, 116.40, 8),
    ('Paris', 'FR', 48.85, 2.35, 1),
    ('Berlin', 'DE', 52.52, 13.41, 1),
    ('Sydney', 'AU', -33.87, 151.21, 10),
    ('Mumbai', 'IN', 19.07, 72.87, 5.5),
    ('Sao Paulo', 'BR', -23.55, -46.63, -3),
    ('Moscow', 'RU', 55.76, 37.62, 3),
    ('Toronto', 'CA', 43.70, -79.40, -5),
    ('Delhi', 'IN', 28.61, 77.21, 5.5),
    ('Shanghai', 'CN', 31.23, 121.47, 8),
    ('Mexico City', 'MX', 19.43, -99.13, -6),
    ('Cape Town', 'ZA', -33.92, 18.42, 2),
    ('Rio de Janeiro', 'BR', -22.91, -43.17, -3),
    ('Seoul', 'KR', 37.57, 126.98, 9),
    ('Amsterdam', 'GB', 52.37, 4.90, 1),
    ('Madrid', 'ES', 40.42, -3.70, 1),
    ('Rome', 'IT', 41.90, 12.49, 1),
]


def _deterministic_seed(city_name: str, date: datetime) -> int:
    key = f"{city_name}_{date.strftime('%Y-%m-%d')}"
    return int(hashlib.md5(key.encode()).hexdigest(), 16)


def get_or_create_city(name: str) -> City:
    city, created = City.objects.get_or_create(
        name__iexact=name,
        defaults={'name': name, 'country': 'US', 'latitude': 0, 'longitude': 0, 'timezone_offset': 0}
    )
    if created:
        for cname, ccountry, clat, clon, ctz in DEFAULT_CITIES:
            if cname.lower() == name.lower():
                city.name = cname
                city.country = ccountry
                city.latitude = clat
                city.longitude = clon
                city.timezone_offset = ctz
                city.save()
                break
    return city


def populate_default_cities():
    for cname, ccountry, clat, clon, ctz in DEFAULT_CITIES:
        City.objects.get_or_create(
            name__iexact=cname,
            defaults={
                'name': cname,
                'country': ccountry,
                'latitude': clat,
                'longitude': clon,
                'timezone_offset': ctz,
            }
        )


def _get_season(date: datetime) -> str:
    month = date.month
    if month in [12, 1, 2]:
        return 'winter'
    elif month in [3, 4, 5]:
        return 'spring'
    elif month in [6, 7, 8]:
        return 'summer'
    else:
        return 'autumn'


def _get_base_temp(city: City, date: datetime) -> float:
    country_base = BASE_TEMPS_BY_COUNTRY.get(city.country, BASE_TEMPS_BY_COUNTRY['default'])
    season = _get_season(date)
    seasonal = SEASONAL_BASE_TEMPS[season]
    base = (seasonal['min'] + seasonal['max']) / 2
    temp_range = seasonal['max'] - seasonal['min']
    country_adjust = (country_base - BASE_TEMPS_BY_COUNTRY['default']) / 10
    return base + country_adjust


def generate_mock_weather(city: City, date: datetime, is_forecast: bool = False) -> dict:
    rng = random.Random(_deterministic_seed(city.name, date))
    base_temp = _get_base_temp(city, date)
    seasonal = SEASONAL_BASE_TEMPS[_get_season(date)]
    daily_range = seasonal['max'] - seasonal['min']

    day_offset = (date - timezone.now().date()).days if hasattr(date, 'date') else 0

    temp_variation = rng.uniform(-daily_range * 0.3, daily_range * 0.3)
    temperature = round(base_temp + temp_variation, 1)

    temp_min = round(temperature - rng.uniform(2, 6), 1)
    temp_max = round(temperature + rng.uniform(2, 6), 1)

    humidity = rng.randint(30, 95)
    if humidity > 80:
        pressure = rng.randint(990, 1015)
    elif humidity > 50:
        pressure = rng.randint(1005, 1025)
    else:
        pressure = rng.randint(1015, 1030)

    wind_speed = round(rng.uniform(1, 25), 1)
    wind_direction = rng.choice([0, 45, 90, 135, 180, 225, 270, 315])

    condition = rng.choice(WEATHER_CONDITIONS)

    if is_forecast and day_offset > 0:
        confidence = max(0.6, 1.0 - (day_offset * 0.07))
    else:
        confidence = 1.0

    return {
        'city': city.name,
        'country': city.country,
        'date': date.strftime('%Y-%m-%d'),
        'day': date.strftime('%A'),
        'temperature': temperature,
        'temperature_min': temp_min,
        'temperature_max': temp_max,
        'humidity': humidity,
        'pressure': pressure,
        'wind_speed': wind_speed,
        'wind_direction': wind_direction,
        'description': condition['description'],
        'icon': condition['icon'],
        'color': condition['color'],
        'confidence': round(confidence, 2) if is_forecast else None,
    }


def generate_current_weather(city: City, date=None) -> dict:
    if date is None:
        date = timezone.now()
    if isinstance(date, datetime):
        date = date.date()
    return generate_mock_weather(city, date, is_forecast=False)


def generate_forecast(city: City, days: int = 5) -> list:
    forecasts = []
    today = timezone.now().date()
    for i in range(days):
        date = today + timedelta(days=i)
        forecasts.append(generate_mock_weather(city, date, is_forecast=True))
    return forecasts


def generate_hourly_forecast(city: City, hours: int = 24) -> list:
    hourly = []
    now = timezone.now()
    for i in range(hours):
        hour = now.hour + i
        date = now.replace(hour=hour % 24)
        temp_offset = (i * 0.5) % 6
        temp = round(_get_base_temp(city, date.date()) + temp_offset, 1)
        rng = random.Random(_deterministic_seed(city.name, date) + i)
        condition = rng.choice(WEATHER_CONDITIONS)
        hourly.append({
            'hour': f"{(hour % 24):02d}:00",
            'temperature': temp,
            'icon': condition['icon'],
            'description': condition['description'],
        })
    return hourly


def generate_historical_data(city: City, days: int = 30) -> list:
    historical = []
    today = timezone.now().date()
    for i in range(days):
        date = today - timedelta(days=i)
        data = generate_mock_weather(city, date, is_forecast=False)
        data['date'] = date.strftime('%Y-%m-%d')
        data['day'] = date.strftime('%A')
        data['timestamp'] = datetime.combine(date, datetime.min.time()).isoformat()
        historical.append(data)
    return historical


def save_weather_to_db(city: City, days: int = 5):
    today = timezone.now().date()
    current = generate_current_weather(city)
    WeatherData.objects.update_or_create(
        city=city, date=today, is_forecast=False,
        defaults={
            'temperature': current['temperature'],
            'temperature_min': current['temperature_min'],
            'temperature_max': current['temperature_max'],
            'humidity': current['humidity'],
            'pressure': current['pressure'],
            'wind_speed': current['wind_speed'],
            'wind_direction': current['wind_direction'],
            'description': current['description'],
            'icon': current['icon'],
        }
    )
    for i in range(1, days):
        date = today + timedelta(days=i)
        forecast = generate_mock_weather(city, date, is_forecast=True)
        WeatherData.objects.update_or_create(
            city=city, date=date, is_forecast=True,
            defaults={
                'temperature': forecast['temperature'],
                'temperature_min': forecast['temperature_min'],
                'temperature_max': forecast['temperature_max'],
                'humidity': forecast['humidity'],
                'pressure': forecast['pressure'],
                'wind_speed': forecast['wind_speed'],
                'wind_direction': forecast['wind_direction'],
                'description': forecast['description'],
                'icon': forecast['icon'],
            }
        )


def get_weather_data(city_name: str, days: int = 5) -> dict:
    city = get_or_create_city(city_name)
    current = generate_current_weather(city)
    forecast = generate_forecast(city, days)
    hourly = generate_hourly_forecast(city)
    return {
        'city': city,
        'current': current,
        'forecast': forecast,
        'hourly': hourly,
    }
