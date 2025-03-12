from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.db.models import Count
from django.db.models.functions import Coalesce
from django.contrib.contenttypes.models import ContentType  # ✅ 추가
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from projectapp.models import Project
from articleapp.models import Article
from communityapp.models import Community
from commentapp.models import Comment
from projectapp.api.serializers import ProjectSerializer
from articleapp.api.serializers import ArticleSerializer
from commentapp.api.serializers import CommentSerializer
from communityapp.api.serializers import CommunitySerializer


class ProjectDetailAPIView(APIView):
    """🏢 프로젝트 상세 API"""
    
    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        
        # 조회수 증가
        project.views += 1
        project.save(update_fields=['views'])

        today = now().date()

        # 공연(Article) 관련 데이터 정렬
        articles = Article.objects.filter(project=project, hide=False).annotate(
            sort_date=Coalesce('datetime', 'date')
        )
        past_articles = articles.filter(sort_date__lt=today).order_by('-sort_date')
        future_articles = articles.filter(sort_date__gte=today).order_by('sort_date')
        all_articles_sorted = list(past_articles)[::-1] + list(future_articles)
        initial_slide_index = len(past_articles) if future_articles else max(0, len(past_articles) - 1)

        # 커뮤니티 게시글
        community_articles = Community.objects.filter(project=project).order_by('-created_at')

        # ✅ 올바르게 ContentType 가져오기
        content_type = ContentType.objects.get_for_model(Project)

        # 댓글 (정렬 방식 적용)
        comments = Comment.objects.filter(content_type=content_type, object_id=project.id) \
                                  .annotate(likes_count=Count('likes'))

        sort = request.GET.get('sort', 'new')
        if sort == 'likes':
            comments = comments.order_by('-likes_count', '-created_at')
        else:
            comments = comments.order_by('-created_at')

        # 데이터 직렬화
        serialized_project = ProjectSerializer(project).data
        serialized_articles = ArticleSerializer(all_articles_sorted, many=True).data
        serialized_community = CommunitySerializer(community_articles, many=True).data
        serialized_comments = CommentSerializer(comments, many=True).data

        return Response({
            'project': serialized_project,
            'articles': serialized_articles,
            'community_articles': serialized_community,
            'comments': serialized_comments,
            'total_comments': comments.count(),
            'total_communities': community_articles.count(),
            'sort': sort,
            'initial_slide_index': initial_slide_index
        }, status=status.HTTP_200_OK)


from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from django.db.models import F
from projectapp.models import Project
from projectapp.api.serializers import ProjectSerializer

class ProjectPagination(PageNumberPagination):
    page_size = 10  # 기본 페이지 크기
    page_size_query_param = 'page_size'
    max_page_size = 100  # 최대 페이지 크기

class ProjectListAPIView(ListAPIView):
    serializer_class = ProjectSerializer
    pagination_class = ProjectPagination

    def get_queryset(self):
        queryset = Project.objects.filter(hide=False)  # 숨겨진 프로젝트 제외

        # 정렬 기준 추가
        order_by = self.request.GET.get('order_by', 'title')  # 기본값: 'title'

        if order_by == 'popularity':
            # 인기순: 좋아요(like) 80%, 조회수(views) 20% 가중치 부여
            queryset = queryset.annotate(
                weighted_score=F('like') * 0.8 + F('views') * 0.2
            ).order_by('-weighted_score')
        else:
            # 기본값: 제목(title) 기준 오름차순 정렬
            queryset = queryset.order_by('title')

        return queryset
    

from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Q, F
from collections import OrderedDict
from projectapp.models import Project
from projectapp.api.serializers import ProjectSerializer

class SearchPagination(PageNumberPagination):
    """🔄 페이지네이션 설정"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class SearchProjectAPIView(APIView):
    """🔍 공연장 검색 API (이름, 주소, 인기순 정렬)"""
    pagination_class = SearchPagination  # ✅ 페이지네이션 클래스 추가

    def get(self, request):
        query = request.GET.get('q', '').strip()  # 검색어에서 앞뒤 공백 제거
        if len(query) < 2:
            return Response({"error": "두 글자 이상 입력해주세요."}, status=400)

        # 🎭 공연장 검색 (이름 & 주소)
        stages = Project.objects.filter(
            Q(title__icontains=query) | 
            Q(address__icontains=query),
            hide=False
        ).distinct()

        # 🔄 중복 제거
        unique_results = list(OrderedDict((stage.id, stage) for stage in stages).values())

        # 🔥 인기순 정렬 (가중치 적용)
        sorted_results = sorted(unique_results, key=lambda x: (x.like * 0.8 + x.views * 0.2), reverse=True)

        # 📌 페이지네이션 적용
        paginator = self.pagination_class()
        page_results = paginator.paginate_queryset(sorted_results, request, view=self)

        if page_results is not None:
            serializer = ProjectSerializer(page_results, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response({"results": []})  # ✅ 빈 응답 방지