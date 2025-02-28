from django.urls import path
from projectapp.api.views import ProjectDetailAPIView, ProjectListAPIView

urlpatterns = [
    path('detail/<int:project_id>/', ProjectDetailAPIView.as_view(), name='project-detail-api'),
    path('list/', ProjectListAPIView.as_view(), name='project_list_api'),  # ✅ 추가
]
