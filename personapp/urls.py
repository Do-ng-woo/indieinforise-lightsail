from personapp.views import PersonListView, PersonCreateView, PersonDetailView, PersonDeleteView, PersonUpdateView, delete_description, person_update_log_view
from django.urls import path, include

app_name = 'personapp'

urlpatterns = [
    path('list/', PersonListView.as_view(template_name='personapp/list.html'), name='list'),
    path('create/', PersonCreateView.as_view(template_name='personapp/create.html'), name='create'),
    path('detail/<int:pk>', PersonDetailView.as_view(template_name='personapp/detail.html'), name='detail'),
    path('delete/<int:pk>', PersonDeleteView.as_view(template_name='personapp/delete.html'), name='delete'),
    path('update/<int:pk>', PersonUpdateView.as_view(template_name='personapp/update.html'), name='update'),
    path('delete_description/', delete_description, name='delete_description'),
    path('persons/<int:pk>/logs/', person_update_log_view, name='person-update-logs'),
    
]