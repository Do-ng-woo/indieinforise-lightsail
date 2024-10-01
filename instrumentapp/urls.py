from instrumentapp.views import InstrumentListView, InstrumentCreateView, InstrumentDetailView, InstrumentDeleteView, InstrumentUpdateView, delete_description, instrument_update_log_view
from django.urls import path, include

app_name = 'instrumentapp'

urlpatterns = [
    path('list/', InstrumentListView.as_view(template_name='instrumentapp/list.html'), name='list'),
    path('create/', InstrumentCreateView.as_view(template_name='instrumentapp/create.html'), name='create'),
    path('detail/<int:pk>', InstrumentDetailView.as_view(template_name='instrumentapp/detail.html'), name='detail'),
    path('delete/<int:pk>', InstrumentDeleteView.as_view(template_name='instrumentapp/delete.html'), name='delete'),
    path('update/<int:pk>', InstrumentUpdateView.as_view(template_name='instrumentapp/update.html'), name='update'),
    path('delete_description/', delete_description, name='delete_description'),
    path('instruments/<int:pk>/logs/', instrument_update_log_view, name='instrument-update-logs'),
    
]