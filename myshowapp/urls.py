from django.urls import path
from . import views
from myshowapp.views import UserPerformanceCreateView, UserPerformanceListView, UserPerformanceUpdateView, UserPerformanceDeleteView, UserPerformanceStampListView
from myshowapp.views import StampUpdateView, MyShowIllustCreateView, MyShowIllustUpdateView, MyShowIllustDetailView, StartIllustView, MyShowIllustDeleteView


app_name = "myshowapp"

urlpatterns = [
    # path('search/', views.search_performances, name='search_performances'),
    path('userperformance/create/<int:pk>/', UserPerformanceCreateView.as_view(), name='userperformance_create'),
    path('card_list/', UserPerformanceListView.as_view(), name='card_list'),
    path('stamp_list/', UserPerformanceStampListView.as_view(), name='stamp_list'),
    path('detail/<int:pk>/', UserPerformanceUpdateView.as_view(), name='userperformance_detail'),
    path('delete/<int:pk>/', UserPerformanceDeleteView.as_view(), name='userperformance_delete'),
    path('stamp/update/<int:pk>', StampUpdateView.as_view(), name='stamp_update'),
    path('create_illust/', MyShowIllustCreateView.as_view(), name='create_myshow_illust'),
    path('update_illust/', MyShowIllustUpdateView.as_view(), name='update_myshow_illust'),
    path('myshowillust/<str:username>/', MyShowIllustDetailView.as_view(), name='detail_myshow_illust'),
    path('start_illust/', StartIllustView.as_view(), name='start_illust'),
    path('delete_illust/', MyShowIllustDeleteView.as_view(), name='delete_myshow_illust'),
]