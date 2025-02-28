from django.urls import path
from artistapp.api.views import ArtistDetailAPIView, ArtistListAPIView

urlpatterns = [
    path('detail/<int:artist_id>/', ArtistDetailAPIView.as_view(), name='artist-detail-api'),
    path('list/', ArtistListAPIView.as_view(), name='artist_list_api'),  # ✅ 추가
]
