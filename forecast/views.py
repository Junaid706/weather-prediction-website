from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db.models import Q

from .models import City, WeatherData, SearchHistory
from .services import (
    get_weather_data, generate_current_weather, generate_forecast,
    generate_hourly_forecast, save_weather_to_db, get_or_create_city,
    populate_default_cities
)
from .ml_service import predict_multi_day, get_prediction_analysis


def home(request):
    if City.objects.count() == 0:
        populate_default_cities()

    recent_searches = SearchHistory.objects.select_related('city').order_by('-searched_at')[:5]
    popular_cities = City.objects.all()[:10]

    context = {
        'recent_searches': recent_searches,
        'popular_cities': popular_cities,
    }
    return render(request, 'forecast/home.html', context)


def weather_lookup(request):
    city_name = request.GET.get('city', '').strip()

    if not city_name:
        messages.error(request, 'Please enter a city name.')
        return redirect('forecast:home')

    city = get_or_create_city(city_name)

    SearchHistory.objects.create(
        city=city,
        ip_address=request.META.get('REMOTE_ADDR', '')
    )

    try:
        data = get_weather_data(city_name, days=5)
    except Exception as e:
        messages.error(request, f'Unable to fetch weather data for "{city_name}".')
        return redirect('forecast:home')

    save_weather_to_db(city, days=5)

    context = {
        'city': data['city'],
        'current': data['current'],
        'forecast': data['forecast'],
        'hourly': data['hourly'],
    }
    return render(request, 'forecast/weather.html', context)


def forecast_detail(request, city_id):
    city = get_object_or_404(City, id=city_id)
    data = get_weather_data(city.name, days=7)

    context = {
        'city': city,
        'current': data['current'],
        'forecast': data['forecast'],
        'hourly': data['hourly'],
    }
    return render(request, 'forecast/weather.html', context)


def prediction(request, city_name=None):
    if city_name:
        city = get_or_create_city(city_name)
    else:
        city_name = request.GET.get('city', 'New York')
        city = get_or_create_city(city_name)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = get_prediction_analysis(city, days=7)
        return JsonResponse({
            'city': data['city'],
            'predictions': data['predictions'],
            'avg_history': data['avg_history'],
            'avg_prediction': data['avg_prediction'],
            'temp_trend': data['temp_trend'],
            'trend_diff': data['trend_diff'],
            'hottest_day': data['hottest_day'],
            'coldest_day': data['coldest_day'],
        })

    data = get_prediction_analysis(city, days=7)
    context = {
        'city': city,
        'predictions': data['predictions'],
        'historical': data['historical'],
        'avg_history': data['avg_history'],
        'avg_prediction': data['avg_prediction'],
        'temp_trend': data['temp_trend'],
        'trend_diff': data['trend_diff'],
        'hottest_day': data['hottest_day'],
        'coldest_day': data['coldest_day'],
    }
    return render(request, 'forecast/prediction.html', context)


def search_history(request):
    history = SearchHistory.objects.select_related('city').order_by('-searched_at')[:50]
    return render(request, 'forecast/history.html', {'history': history})


def api_weather(request, city_name):
    data = get_weather_data(city_name, days=5)
    return JsonResponse({
        'city': data['city'].name,
        'country': data['city'].country,
        'current': data['current'],
        'forecast': data['forecast'],
    })


def api_prediction(request, city_name):
    city = get_or_create_city(city_name)
    data = get_prediction_analysis(city, days=7)
    return JsonResponse({
        'city': data['city'],
        'predictions': data['predictions'],
        'avg_history': data['avg_history'],
        'avg_prediction': data['avg_prediction'],
        'trend': data['temp_trend'],
    })


def about(request):
    return render(request, 'forecast/about.html')
