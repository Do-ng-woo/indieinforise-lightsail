from singapp.views import SingListView, SingCreateView, SingDetailView, SingDeleteView, SingUpdateView, delete_description, sing_update_log_view
from django.urls import path, include

app_name = 'singapp'

urlpatterns = [
    path('list/', SingListView.as_view(template_name='singapp/list.html'), name='list'),
    path('create/', SingCreateView.as_view(template_name='singapp/create.html'), name='create'),
    path('detail/<int:pk>', SingDetailView.as_view(template_name='singapp/detail.html'), name='detail'),
    path('delete/<int:pk>', SingDeleteView.as_view(template_name='singapp/delete.html'), name='delete'),
    path('update/<int:pk>', SingUpdateView.as_view(template_name='singapp/update.html'), name='update'),
    path('delete_description/', delete_description, name='delete_description'),
    path('sings/<int:pk>/logs/', sing_update_log_view, name='sing-update-logs'),
    
]