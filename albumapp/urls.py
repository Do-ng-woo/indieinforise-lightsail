from albumapp.views import AlbumListView, AlbumCreateView, AlbumDetailView, AlbumDeleteView, AlbumUpdateView, delete_description, album_update_log_view, get_songs_by_artist
from django.urls import path, include

app_name = 'albumapp'

urlpatterns = [
    path('list/', AlbumListView.as_view(template_name='albumapp/list.html'), name='list'),
    path('create/', AlbumCreateView.as_view(template_name='albumapp/create.html'), name='create'),
    path('detail/<int:pk>', AlbumDetailView.as_view(template_name='albumapp/detail.html'), name='detail'),
    path('delete/<int:pk>', AlbumDeleteView.as_view(template_name='albumapp/delete.html'), name='delete'),
    path('update/<int:pk>', AlbumUpdateView.as_view(template_name='albumapp/update.html'), name='update'),
    path('delete_description/', delete_description, name='delete_description'),
    path('albums/<int:pk>/logs/', album_update_log_view, name='album-update-logs'),
    path('get-songs-by-artist/<int:artist_id>/', get_songs_by_artist, name='get_songs_by_artist'),
    
]