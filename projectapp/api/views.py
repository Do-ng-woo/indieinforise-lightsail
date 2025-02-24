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
