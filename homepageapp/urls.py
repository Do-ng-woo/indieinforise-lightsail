from django.urls import path
from django.views.generic import TemplateView

from homepageapp.views import HomepageCreateView, HomepageDetailView, HomepageView

app_name = "homepageapp"

urlpatterns = [
    path('create/', HomepageCreateView.as_view(template_name='homepageapp/create.html'), name='create'),
    path('detail/<int:pk>/', HomepageDetailView.as_view(template_name='homepageapp/detail.html'), name='detail'),
    path('homepage/', HomepageView.as_view(template_name='homepageapp/homepage.html'), name='main'),
    
        
    
]