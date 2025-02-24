from rest_framework import serializers
from accountapp.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    """👤 사용자 정보 Serializer"""
    image = serializers.SerializerMethodField()  # 프로필 이미지 URL 처리

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'nickname', 'gender', 'birth_date',
            'purpose_of_use', 'image', 'message', 'level', 'points', 
            'post_count', 'comment_count', 'performance_points', 
            'privacy_policy_agreement', 'signup_method'
        ]

    def get_image(self, obj):
        """🖼️ 프로필 이미지 URL 반환"""
        if obj.image:
            return obj.image.url
        return "/media/myarticleimage/default_profile.jpg"
