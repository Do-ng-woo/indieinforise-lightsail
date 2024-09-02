from django.urls import path
from profileapp.views import ProfileCreateView, ProfileUpdateView
from django.urls import path
from . import views

app_name ='profileapp'

urlpatterns =[
    path('create/', ProfileCreateView.as_view(), name='create'),
    path('update/<int:pk>', ProfileUpdateView.as_view(), name='update'),
]