import random
from datetime import timedelta
from django.db import models
from django.utils import timezone


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=5, decimal_places=2)
    longitude = models.DecimalField(max_digits=5, decimal_places=2)
    timezone_offset = models.IntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.country}"


class WeatherData(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='weather_data')
    date = models.DateField()
    temperature = models.DecimalField(max_digits=4, decimal_places=1)
    temperature_min = models.DecimalField(max_digits=4, decimal_places=1)
    temperature_max = models.DecimalField(max_digits=4, decimal_places=1)
    humidity = models.IntegerField()
    pressure = models.IntegerField()
    wind_speed = models.DecimalField(max_digits=4, decimal_places=1)
    wind_direction = models.IntegerField()
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=10, default='01d')
    is_forecast = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['city', 'date', 'is_forecast']

    def __str__(self):
        return f"{self.city.name} - {self.date} - {self.temperature}°C"


class SearchHistory(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    searched_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-searched_at']

    def __str__(self):
        return f"{self.city.name} searched at {self.searched_at}"


class TemperatureReading(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='temperature_readings')
    timestamp = models.DateTimeField()
    temperature = models.DecimalField(max_digits=4, decimal_places=1)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.city.name} @ {self.timestamp}: {self.temperature}°C"
