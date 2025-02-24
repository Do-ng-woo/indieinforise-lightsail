from django.urls import path
from projectapp.api.views import ProjectDetailAPIView

urlpatterns = [
    path('detail/<int:project_id>/', ProjectDetailAPIView.as_view(), name='project-detail-api'),
]
