from genreapp.views import GenreListView, GenreCreateView, GenreDetailView, GenreDeleteView, GenreUpdateView, delete_description, genre_update_log_view
from django.urls import path, include

app_name = 'genreapp'

urlpatterns = [
    path('list/', GenreListView.as_view(template_name='genreapp/list.html'), name='list'),
    path('create/', GenreCreateView.as_view(template_name='genreapp/create.html'), name='create'),
    path('detail/<int:pk>', GenreDetailView.as_view(template_name='genreapp/detail.html'), name='detail'),
    path('delete/<int:pk>', GenreDeleteView.as_view(template_name='genreapp/delete.html'), name='delete'),
    path('update/<int:pk>', GenreUpdateView.as_view(template_name='genreapp/update.html'), name='update'),
    path('delete_description/', delete_description, name='delete_description'),
    path('genres/<int:pk>/logs/', genre_update_log_view, name='genre-update-logs'),
    
]