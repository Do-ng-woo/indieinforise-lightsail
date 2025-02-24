from rest_framework import serializers
from personapp.models import Person, Description
from instrumentapp.models import Instrument

class PersonSerializer(serializers.ModelSerializer):
    """👤 인물 직렬화"""
    writer = serializers.StringRelatedField()  # 작성자 닉네임 반환
    sub_titles = serializers.SerializerMethodField()
    instruments = serializers.SerializerMethodField()
    descriptions = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = [
            'id', 'writer', 'title', 'image', 'description',
            'sub_titles', 'instruments', 'descriptions',
            'like', 'views', 'comment_count',
            'created_at', 'updated_at'
        ]

    def get_sub_titles(self, obj):
        """📌 인물의 부제목 리스트 반환"""
        return [subtitle.name for subtitle in obj.sub_titles.all()]

    def get_instruments(self, obj):
        """🎸 다룰 수 있는 악기 목록 반환"""
        return [{"id": inst.id, "name": inst.title, "image": inst.image.url} for inst in obj.instruments.all()]

    def get_descriptions(self, obj):
        """📝 인물 설명 반환"""
        return [{"id": desc.id, "name": desc.name, "text": desc.text} for desc in obj.detailed_descriptions.all()]
