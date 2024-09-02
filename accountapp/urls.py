from django.urls import path
from accountapp.views import hello_world, AccountCreateView, AccountDetailView, AccountUpdateView, AccountDeleteView, CustomLoginView
from accountapp.views import add_favorite_search, delete_favorite_keyword, get_field_data
from . import views
from django.contrib.auth.views import LoginView, LogoutView


app_name = "accountapp"

urlpatterns = [    
    path('login/', CustomLoginView.as_view(template_name='accountapp/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('create/', AccountCreateView.as_view(), name='create'),
    path('detail/<int:pk>', AccountDetailView.as_view(), name='detail'),
    path('update/<int:pk>', AccountUpdateView.as_view(), name='update'),
    path('delete/<int:pk>', AccountDeleteView.as_view(), name='delete'),
    path('add_favorite_search/', views.add_favorite_search, name='add_favorite_search'),
    path('delete_favorite_keyword/<int:keyword_id>/', views.delete_favorite_keyword, name='delete_favorite_keyword'),
    path('get-field-data/', get_field_data, name='get_field_data'),
    
]
