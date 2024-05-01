from django.views.generic import CreateView, DetailView, TemplateView
from django.contrib.auth.views import LoginView
from django.shortcuts import HttpResponseRedirect, render
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomUserCreationForm, CityForm
from .models import CustomUser
from datetime import datetime
import requests
import os

class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
                return HttpResponseRedirect(self.get_success_url())
            else:
                messages.error(self.request, "This account is inactive.")
        else:
            messages.error(self.request, "Invalid username or password.")
        return render(self.request, self.template_name, {'form': form})

    def get_success_url(self):
        return reverse_lazy('authentication:user_page', kwargs={'pk': self.request.user.pk})

class CustomSignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('authentication:login')
    template_name = 'authentication/signup.html'

class InitialPageView(TemplateView):
    template_name = 'authentication/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class UserPageView(DetailView):
    model = CustomUser
    template_name = 'authentication/user_page.html'
    form_class = CityForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        lat, lon = (52.2053, 0.1218) if not user.latitude or not user.longitude else (user.latitude, user.longitude)

        context.update({
            'current_weather': self.fetch_current_weather(lat, lon),
            'forecast': self.fetch_forecast(lat, lon),
            'city_form': CityForm(instance=user)
        })
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CityForm(request.POST, instance=self.object)
        if form.is_valid():
            new_city = form.cleaned_data['city']
            lat, lon = self.geocode_city(new_city)
            if lat and lon:
                self.object.latitude = lat
                self.object.longitude = lon
                self.object.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            context = self.get_context_data()
            context['city_form'] = form
            return render(request, self.template_name, context)

    def get_success_url(self):
        return reverse_lazy('authentication:user_page', kwargs={'pk': self.object.pk})

    def geocode_city(self, city_name):
        api_key = os.getenv('WEATHER_API_KEY')
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&appid={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]['lat'], data[0]['lon']
        return None, None

    def fetch_current_weather(self, lat, lon):
        api_key = os.getenv('WEATHER_API_KEY')
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return {
                'temperature': data['current']['temp'],
                'description': data['current']['weather'][0]['description']
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching current weather data: {e}")
            return {'error': 'Failed to fetch weather data'}

    def fetch_forecast(self, lat, lon):
        api_key = os.getenv('WEATHER_API_KEY')
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        forecast_data = []
        try:
            response = requests.get(url)
            response.raise_for_status()
            daily_forecasts = response.json()['daily']
            for forecast in daily_forecasts:
                forecast_data.append({
                    'date': datetime.fromtimestamp(forecast['dt']).strftime('%Y-%m-%d'),
                    'temperature': forecast['temp']['day'],
                    'description': forecast['weather'][0]['description']
                })
        except requests.exceptions.RequestException as e:
            print(f"Error fetching forecast data: {e}")
        return forecast_data
