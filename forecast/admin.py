from django.contrib import admin
from .models import City, WeatherData, SearchHistory, TemperatureReading


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'latitude', 'longitude']
    search_fields = ['name', 'country']


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['city', 'date', 'temperature', 'description', 'is_forecast']
    list_filter = ['is_forecast', 'city']
    search_fields = ['city__name']


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['city', 'searched_at', 'ip_address']
    list_filter = ['searched_at']
    search_fields = ['city__name', 'ip_address']


@admin.register(TemperatureReading)
class TemperatureReadingAdmin(admin.ModelAdmin):
    list_display = ['city', 'timestamp', 'temperature']
    list_filter = ['city']
    search_fields = ['city__name']
