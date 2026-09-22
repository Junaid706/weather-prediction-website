from django.urls import path
from . import views

app_name = 'forecast'

urlpatterns = [
    path('', views.home, name='home'),
    path('weather/', views.weather_lookup, name='weather_lookup'),
    path('weather/<int:city_id>/', views.forecast_detail, name='forecast_detail'),
    path('prediction/', views.prediction, name='prediction'),
    path('prediction/<str:city_name>/', views.prediction, name='prediction_city'),
    path('history/', views.search_history, name='search_history'),
    path('about/', views.about, name='about'),
    path('api/weather/<str:city_name>/', views.api_weather, name='api_weather'),
    path('api/prediction/<str:city_name>/', views.api_prediction, name='api_prediction'),
]
