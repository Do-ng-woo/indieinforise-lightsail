from projectapp.views import ProjectListView, ProjectCreateView, ProjectDetailView, ProjectDeleteView, ProjectUpdateView, project_delete_description, events_api, project_update_log_view
from django.urls import path, include
from django.views.generic import TemplateView

app_name = 'projectapp'

urlpatterns = [
    path('list/', ProjectListView.as_view(template_name='projectapp/list.html'), name='list'),
    path('create/', ProjectCreateView.as_view(template_name='projectapp/create.html'), name='create'),
    path('detail/<int:pk>', ProjectDetailView.as_view(template_name='projectapp/detail.html'), name='detail'),
    path('delete/<int:pk>', ProjectDeleteView.as_view(template_name='projectapp/delete.html'), name='delete'),
    path('update/<int:pk>', ProjectUpdateView.as_view(template_name='projectapp/update.html'), name='update'),
    path('project_delete_description/', project_delete_description, name='project_delete_description'),
    path('path-to-events-api/', events_api, name='events-api'),
    path('projects/<int:pk>/logs/', project_update_log_view, name='project-update-logs'),
    
]