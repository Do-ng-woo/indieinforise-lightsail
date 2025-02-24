from rest_framework import serializers
from projectapp.models import Project, Description, ProjectUpdateLog

class ProjectSerializer(serializers.ModelSerializer):
    """🏢 공연장(Project) 직렬화"""
    writer = serializers.StringRelatedField()  # 작성자 닉네임 반환
    sub_titles = serializers.SerializerMethodField()
    descriptions = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'writer', 'title', 'image', 'description',
            'sub_titles', 'latitude', 'longitude', 'address',
            'like', 'views', 'comment_count',
            'created_at', 'hide',
            'descriptions',  # ✅ 여기에 descriptions 필드를 추가
        ]
    
    def get_sub_titles(self, obj):
        """📌 공연장의 부제목 리스트 반환"""
        return [subtitle.name for subtitle in obj.sub_titles.all()]
    
    def get_descriptions(self, obj):
        """📝 공연장 설명 반환"""
        return [{"id": desc.id, "name": desc.name, "text": desc.text} for desc in obj.detailed_descriptions.all()]
    
    def get_image(self, obj):
        """🏞 공연장 이미지 URL 반환"""
        request = self.context.get('request')

        if obj.image:
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url  # request가 없는 경우 절대 경로만 반환

        return None  # 이미지가 없을 경우 None 반환


class ProjectUpdateLogSerializer(serializers.ModelSerializer):
    """📝 공연장 업데이트 기록 직렬화"""
    updated_by = serializers.StringRelatedField()

    class Meta:
        model = ProjectUpdateLog
        fields = ['id', 'updated_by', 'updated_at', 'update_description', 'hide']


class DescriptionSerializer(serializers.ModelSerializer):
    """📌 공연장 상세 설명 직렬화"""
    class Meta:
        model = Description
        fields = ['id', 'project', 'name', 'text']
