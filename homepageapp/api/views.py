# homepageapp/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models.functions import Coalesce
from homepageapp.models import Article, Artist, Project
from articleapp.api.serializers import ArticleSerializer
from artistapp.api.serializers import ArtistSerializer
from projectapp.api.serializers import ProjectSerializer
class HomeDataAPIView(APIView):
    """
    홈페이지 데이터를 제공하는 REST API 뷰
    """
    def get(self, request, *args, **kwargs):
        latest_articles = Article.objects.annotate(
            sort_date=Coalesce('datetime', 'date')
        ).filter(sort_date__gte=timezone.now(), hide=False).order_by('sort_date')[:4]
        popular_artists = Artist.objects.filter(hide=False).order_by('-like')[:6]
        popular_projects = Project.objects.filter(hide=False).order_by('-like')[:6]

        return Response({
            'latest_articles': ArticleSerializer(latest_articles, many=True).data,
            'popular_artists': ArtistSerializer(popular_artists, many=True).data,
            'popular_projects': ProjectSerializer(popular_projects, many=True).data,
        })
