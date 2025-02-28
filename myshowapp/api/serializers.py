from rest_framework import serializers
from articleapp.models import Article  # ✅ Article 모델 임포트
from myshowapp.models import UserPerformance  # ✅ UserPerformance 모델 임포트

class UserPerformanceSerializer(serializers.ModelSerializer):
    """🎭 사용자의 공연 관람 정보 Serializer"""
    
    article_title = serializers.CharField(source='article.title', read_only=True)  # 공연 제목
    article_image = serializers.SerializerMethodField()  # 공연 이미지
    stamp_image_url = serializers.SerializerMethodField()  # 스탬프 이미지 URL

    class Meta:
        model = UserPerformance
        fields = [
            'id', 'user', 'article', 'article_title', 'article_image', 'status', 
            'rating', 'memo', 'running_time', 'stamp_image_url', 'stamp'
        ]
    
    def get_article_image(self, obj):
        """🎭 공연 포스터 이미지 URL 반환"""
        if obj.article.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.article.image.url) if request else obj.article.image.url
        return None  # 이미지가 없으면 None 반환

    def get_stamp_image_url(self, obj):
        """📌 스탬프 이미지 URL 반환"""
        if obj.stamp_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.stamp_image.url) if request else obj.stamp_image.url
        return None  # 스탬프 이미지가 없으면 None 반환
