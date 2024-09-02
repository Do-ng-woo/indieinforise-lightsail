import os
import django
import pandas as pd
from django.core.files import File
from django.core.files.images import ImageFile
# Django 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Renaissance.settings")
django.setup()

from django.contrib.auth.models import User
from artistapp.models import Artist, Description, Subtitle
from django.contrib.auth import get_user_model


User = get_user_model()

def import_data_to_descriptions(file_path):
    df = pd.read_csv(file_path)
    
    for index, row in df.iterrows():
        artist_names = [name.strip() for name in row['Artist'].split(',')]
        description_name = row['Name']
        description_text = row['Text']
        
        user = User.objects.all()[1]
        
        for artist_name in artist_names:
            # 아티스트 이름을 서브타이틀로 사용
            subtitles = [artist_name]  # 실제 사용 시 다른 서브타이틀 조건을 적용할 수 있습니다.
            artist, created = Artist.objects.get_or_create_artist_by_subtitles(
                artist_name,
                subtitles,
                defaults={
                    'image': 'default_image/default_artist.jpg',  # 실제 경로로 변경 필요
                    'description': '기본 설명 추가',  # 초기 설명 설정
                    'writer': user #위에서 설정함
                }
            )
                
            # Description 객체 생성 또는 업데이트
            description, created = Description.objects.update_or_create(
                artist=artist,
                name=description_name,
                defaults={'text': description_text}
            )
            
            # 처리 결과 로그
            print(f"{'생성' if created else '업데이트'}: {artist.title} - {description_name}")

# 파일 경로 지정
file_path = 'artistapp/mydata/artist_description_data.csv'
import_data_to_descriptions(file_path)
