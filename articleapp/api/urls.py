from django.urls import path
from articleapp.api.views import ArticleDetailAPIView

urlpatterns = [
    path('detail/<int:article_id>/', ArticleDetailAPIView.as_view(), name='article_detail_api'),
]
