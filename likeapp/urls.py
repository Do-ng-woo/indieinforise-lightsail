from django.urls import path
from likeapp.views import LikeArticleView
from likeapp.views import LikeCommunityView, LikeArtistView, LikeProjectView, LikePersonView, LikeSingView, LikeAlbumView, LikeGenreView,LikeInstrumentView

app_name = "likeapp"

urlpatterns = [
    path('article/like/<int:pk>', LikeArticleView.as_view(), name='article_like'),
    path('community/like/<int:pk>', LikeCommunityView.as_view(), name='community_like'),
    path('artist/like/<int:pk>', LikeArtistView.as_view(), name='artist_like'),
    path('project/like/<int:pk>', LikeProjectView.as_view(), name='project_like'),
    path('person/like/<int:pk>', LikePersonView.as_view(), name='person_like'),
    path('sing/like/<int:pk>', LikeSingView.as_view(), name='sing_like'),
    path('album/like/<int:pk>', LikeAlbumView.as_view(), name='album_like'),
    path('genre/like/<int:pk>', LikeGenreView.as_view(), name='genre_like'),
    path('instrument/like/<int:pk>', LikeInstrumentView.as_view(), name='instrument_like'),
    
]