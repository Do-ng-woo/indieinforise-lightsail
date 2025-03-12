from django.urls import path
from projectapp.api.views import ProjectDetailAPIView, ProjectListAPIView, SearchProjectAPIView

urlpatterns = [
    path('detail/<int:project_id>/', ProjectDetailAPIView.as_view(), name='project-detail-api'),
    path('list/', ProjectListAPIView.as_view(), name='project_list_api'),  # ✅ 추가
    path('search/', SearchProjectAPIView.as_view(), name='article_search_api'),  # ✅ 검색 API 추가
]
