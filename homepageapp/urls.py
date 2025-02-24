from django.urls import path,include
from django.views.generic import TemplateView

from homepageapp.views import HomepageCreateView, HomepageDetailView, HomepageView

app_name = "homepageapp"

urlpatterns = [
    path('create/', HomepageCreateView.as_view(template_name='homepageapp/create.html'), name='create'),
    path('detail/<int:pk>/', HomepageDetailView.as_view(template_name='homepageapp/detail.html'), name='detail'),
    path('homepage/', HomepageView.as_view(template_name='homepageapp/homepage.html'), name='main'),
    path('storypage/', TemplateView.as_view(template_name='homepageapp/storypage.html'), name='storypage'),
    path('api/', include('homepageapp.api.urls')),  # ✅ API 폴더의 urls.py 포함
]
    
        
    
