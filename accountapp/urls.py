from django.urls import path, include
from accountapp.views import hello_world, AccountCreateView, AccountDetailView, AccountUpdateView, AccountDeleteView, CustomLoginView
from accountapp.views import add_favorite_search, delete_favorite_keyword, get_field_data, privacy_policy
from . import views
from accountapp.views import CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
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
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('send-verification-email/', views.send_verification_email_view, name='send_verification_email'),
    # Password reset URLs
    # Password reset URLs
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('api/', include('accountapp.api.urls')), 
]