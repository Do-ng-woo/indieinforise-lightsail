# homepageapp/api_urls.py
from django.urls import path
from homepageapp.api.views import HomeDataAPIView

urlpatterns = [
    path('home/', HomeDataAPIView.as_view(), name='home-data-api'),
]
