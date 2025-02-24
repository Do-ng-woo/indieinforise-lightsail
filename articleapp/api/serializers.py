from rest_framework import serializers
from articleapp.models import Article
from artistapp.models import Artist
from projectapp.models import Project
from commentapp.models import Comment

class ArticleSerializer(serializers.ModelSerializer):
    """🎭 공연 정보 Serializer"""
    artists = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'image', 'content', 'date', 'datetime', 'running_time', 
            'location', 'artists', 'views', 'comment_count', 'like', 'link', 'comments'
        ]

    def get_artists(self, obj):
        """🎤 공연 참여 아티스트 목록 반환"""
        return [{"id": artist.id, "name": artist.title, "image": artist.image.url if artist.image else "/media/default_artist.jpg"} for artist in obj.artist.all()]

    def get_location(self, obj):
        """🎪 공연 장소 반환 (첫 번째 프로젝트만 사용)"""
        return obj.project.first().title if obj.project.exists() else "공연장 미정"

    def get_image(self, obj):
        """🖼️ 이미지 URL 반환"""
        return obj.image.url if obj.image else "/media/default_article.jpg"

    def get_comments(self, obj):
        """💬 최신 댓글 목록 반환 (최대 5개)"""
        return [{"id": c.id, "content": c.content} for c in Comment.objects.filter(object_id=obj.id).order_by('-created_at')[:5]]
