"""Renaissance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from articleapp.views import ArticleListView
from .views import redirect_to_detail_view

urlpatterns = [
    path('', redirect_to_detail_view, name='home'),
    
    path('admin/', admin.site.urls),
    path('accounts/', include('accountapp.urls')),
    path('profiles/', include('profileapp.urls')),
    path('articles/', include('articleapp.urls')),
    path('comments/', include('commentapp.urls')),
    path('projects/', include('projectapp.urls')),
    path('subscribe/', include('subscribeapp.urls')),
    path('artists/', include('artistapp.urls')),
    path('likes/', include('likeapp.urls')),
    path('persons/', include('personapp.urls')),
    path('homepages/', include('homepageapp.urls')),
    path('community/', include('communityapp.urls')),
    path('sings/', include('singapp.urls')),
    path('albums/', include('albumapp.urls')),
    path('genres/', include('genreapp.urls')),
    path('searchs/', include('searchapp.urls')),
    path('instrumnets/', include('instrumentapp.urls')),
    path('myshows/', include('myshowapp.urls'))
    
    
    
    
        
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
