from django.urls import path
from django.views.generic import TemplateView

from communityapp.views import CommunityCreateView, CommunityDetailView, CommunityUpdateView, CommunityDeleteView, CommunityListView, file_upload

app_name = "communityapp"

urlpatterns = [
    path('list/', CommunityListView.as_view(template_name='communityapp/list.html'), name='list'),
    path('create/', CommunityCreateView.as_view(template_name='communityapp/create.html'), name='create'),
    path('detail/<int:pk>', CommunityDetailView.as_view(template_name='communityapp/detail.html'), name='detail'),
    path('update/<int:pk>', CommunityUpdateView.as_view(template_name='communityapp/update.html'), name='update'),
    path('delete/<int:pk>', CommunityDeleteView.as_view(template_name='communityapp/delete.html'), name='delete'),
    path('file-upload/', file_upload, name='file_upload'),
        
    
]