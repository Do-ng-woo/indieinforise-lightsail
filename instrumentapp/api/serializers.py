from rest_framework import serializers
from instrumentapp.models import Instrument, Description

class InstrumentSerializer(serializers.ModelSerializer):
    """🎸 악기 직렬화"""
    writer = serializers.StringRelatedField()  # 작성자 닉네임 반환
    sub_titles = serializers.SerializerMethodField()
    descriptions = serializers.SerializerMethodField()

    class Meta:
        model = Instrument
        fields = [
            'id', 'writer', 'title', 'image', 'content',
            'sub_titles', 'descriptions',
            'like', 'views', 'comment_count',
            'created_at', 'updated_at'
        ]

    def get_sub_titles(self, obj):
        """📌 악기의 부제목 리스트 반환"""
        return [subtitle.name for subtitle in obj.sub_titles.all()]

    def get_descriptions(self, obj):
        """📝 악기 설명 반환"""
        return [{"id": desc.id, "name": desc.name, "text": desc.text} for desc in obj.detailed_descriptions.all()]
