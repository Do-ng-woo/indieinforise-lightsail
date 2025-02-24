from django.urls import path, include
from django.views.generic import TemplateView

from articleapp.views import ArticleCreateView, ArticleDetailView, ArticleUpdateView, ArticleDeleteView, ArticleListView, ArticleEventsAPIView, CalendarDetailAPIView, article_update_log_view

app_name = "articleapp"

urlpatterns = [
    path('list/', ArticleListView.as_view(template_name='articleapp/list.html'), name='list'),
    path('create/', ArticleCreateView.as_view(template_name='articleapp/create.html'), name='create'),
    path('detail/<int:pk>', ArticleDetailView.as_view(template_name='articleapp/detail.html'), name='detail'),
    path('update/<int:pk>', ArticleUpdateView.as_view(template_name='articleapp/update.html'), name='update'),
    path('delete/<int:pk>', ArticleDeleteView.as_view(template_name='articleapp/delete.html'), name='delete'),
    path('calendar/', TemplateView.as_view(template_name='articleapp/calendar.html'), name='calendar'),
    path('api/events/', ArticleEventsAPIView.as_view(), name='api-events'),
    path('calendar_detail/', CalendarDetailAPIView.as_view(), name='calendar_detail'),  # 경로 이름 변경
    path('articles/<int:pk>/logs/', article_update_log_view, name='article-update-logs'),
    path('api/', include('articleapp.api.urls')),  
]
    
        
