from artistapp.views import ArtistListView, ArtistCreateView, ArtistDetailView, ArtistDeleteView, ArtistUpdateView
from artistapp.views import HonoraryEntryListView, delete_description, artist_update_log_view, get_persons_by_instrument, artist_use_points
from django.urls import path, include

app_name = 'artistapp'

urlpatterns = [
    path('list/', ArtistListView.as_view(template_name='artistapp/list.html'), name='list'),
    path('create/', ArtistCreateView.as_view(template_name='artistapp/create.html'), name='create'),
    path('detail/<int:pk>', ArtistDetailView.as_view(template_name='artistapp/detail.html'), name='detail'),
    path('delete/<int:pk>', ArtistDeleteView.as_view(template_name='artistapp/delete.html'), name='delete'),
    path('update/<int:pk>', ArtistUpdateView.as_view(template_name='artistapp/update.html'), name='update'),
    path('delete_description/', delete_description, name='delete_description'),
    path('artists/<int:pk>/logs/', artist_update_log_view, name='artist-update-logs'),
    path('get-persons-by-instrument/<int:instrument_id>/', get_persons_by_instrument, name='get_persons_by_instrument'),
    path('artists/<int:artist_id>/use_points/', artist_use_points, name='use_points'),
    path('honorary_list/', HonoraryEntryListView.as_view(), name='honorary_list'),
]