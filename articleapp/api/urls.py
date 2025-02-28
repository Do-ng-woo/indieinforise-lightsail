from django.urls import path
from articleapp.api.views import ArticleDetailAPIView, ArticleListAPIView

urlpatterns = [
    path('detail/<int:article_id>/', ArticleDetailAPIView.as_view(), name='article_detail_api'),
    path('list/', ArticleListAPIView.as_view(), name='article_list_api'),  # ✅ 추가
]
