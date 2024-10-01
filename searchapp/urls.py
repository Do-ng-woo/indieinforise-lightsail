from django.urls import path
from searchapp.views import search_view, load_more_data

app_name = "searchapp"

urlpatterns = [
    path('search/', search_view, name='search'),  # 검색 페이지 URL
    path('load-more-data/<str:model_name>/', load_more_data, name='load_more_data'),
]