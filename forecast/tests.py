from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import City, WeatherData, SearchHistory
from .services import generate_mock_weather, get_weather_data, populate_default_cities
from .ml_service import predict_multi_day, get_prediction_analysis


class CityModelTest(TestCase):
    def setUp(self):
        populate_default_cities()

    def test_city_str(self):
        city = City.objects.get(name="London")
        self.assertEqual(str(city), "London, GB")

    def test_cities_populated(self):
        self.assertTrue(City.objects.count() >= 10)


class WeatherServiceTest(TestCase):
    def setUp(self):
        populate_default_cities()

    def test_generate_mock_weather_deterministic(self):
        city = City.objects.get(name="London")
        data1 = generate_mock_weather(city, timezone.now().date())
        data2 = generate_mock_weather(city, timezone.now().date())
        self.assertEqual(data1['temperature'], data2['temperature'])

    def test_weather_data_structure(self):
        city = City.objects.get(name="New York")
        data = generate_mock_weather(city, timezone.now().date())
        self.assertIn('temperature', data)
        self.assertIn('humidity', data)
        self.assertIn('description', data)
        self.assertIn('icon', data)

    def test_forecast_has_correct_days(self):
        city = City.objects.get(name="Tokyo")
        data = get_weather_data("Tokyo", days=5)
        self.assertEqual(len(data['forecast']), 5)

    def test_hourly_forecast(self):
        city = City.objects.get(name="Paris")
        data = get_weather_data("Paris")
        self.assertEqual(len(data['hourly']), 24)


class MLPredictionTest(TestCase):
    def setUp(self):
        populate_default_cities()

    def test_prediction_returns_data(self):
        city = City.objects.get(name="London")
        predictions = predict_multi_day(city, days=7)
        self.assertEqual(len(predictions), 7)
        for p in predictions:
            self.assertIn('predicted_temperature', p)
            self.assertIn('confidence', p)

    def test_analysis_structure(self):
        city = City.objects.get(name="Berlin")
        analysis = get_prediction_analysis(city, days=7)
        self.assertIn('predictions', analysis)
        self.assertIn('historical', analysis)
        self.assertIn('avg_history', analysis)
        self.assertIn('avg_prediction', analysis)


class ViewTest(TestCase):
    def setUp(self):
        populate_default_cities()

    def test_home_view(self):
        response = self.client.get(reverse('forecast:home'))
        self.assertEqual(response.status_code, 200)

    def test_weather_lookup_view(self):
        response = self.client.get(reverse('forecast:weather_lookup') + '?city=London')
        self.assertEqual(response.status_code, 200)

    def test_prediction_view(self):
        response = self.client.get(reverse('forecast:prediction'))
        self.assertEqual(response.status_code, 200)

    def test_api_weather_view(self):
        response = self.client.get(reverse('forecast:api_weather', args=['London']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['city'], 'London')
        self.assertEqual(response.json()['country'], 'GB')

    def test_search_history_creates_record(self):
        initial_count = SearchHistory.objects.count()
        self.client.get(reverse('forecast:weather_lookup') + '?city=Tokyo')
        self.assertEqual(SearchHistory.objects.count(), initial_count + 1)
