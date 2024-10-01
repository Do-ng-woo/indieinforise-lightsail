import os
import django
from django.core.files import File
from django.core.files.images import ImageFile

# DJANGO_SETTINGS_MODULE 환경 변수를 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Renaissance.settings")

# Django 설정을 로드
django.setup()

import pandas as pd
from datetime import datetime
from singapp.models import Sing
from artistapp.models import Artist, Subtitle
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

def import_data_to_sings(file_path):
    df = pd.read_csv(file_path)
    default_image_path = 'media/defalt_image/Renaissance_default_1.jpg'

    for index, row in df.iterrows():
        title = row['title']
        artist_names = [name.strip() for name in row['artist'].split(',')]
        image_path = row['image_path']
        lyrics = row['lyrics']

        # 사용자를 임의로 선택하거나 고정할 수 있습니다.
        user = User.objects.all()[0]

        # 아티스트를 추가하려면 해당 필드들의 데이터를 가져와서 추가합니다.
        artists = []
        for name in artist_names:
            subtitles = [name]  # Subtitle로 아티스트 이름을 사용
            artist, created = Artist.objects.get_or_create_artist_by_subtitles(
                name,
                subtitles,
                defaults={
                    'image': 'defalt_image/defalt_artist.jpg',
                    'description': '설명을 추가해 주세요',
                    'writer': user
                }
            )

            artists.append(artist)

             # Debug 출력
            print(f"Artist: {artist.title}, Created: {created}")

        # 기존 Sing 중복 검사 (title과 artist들이 모두 일치하는지 확인)
        existing_sing = Sing.objects.filter(title=title, artist__in=artists).first()
        if existing_sing:
            print(f"Title이 '{title}'이고 Artist가 '{', '.join(artist_names)}'인 Sing은 이미 존재합니다. 생성을 건너뜁니다.")
            continue

        # Sing 모델에 데이터 저장
        sing = Sing.objects.create(
            writer=user,
            title=title,
            content=lyrics,
        )

        sing.artist.set(artists)

        # 이미지 파일 등록
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as image_file:
                sing.image.save(os.path.basename(image_path), File(image_file))
        else:
            # 기본 이미지 사용
            with open(default_image_path, 'rb') as default_image_file:
                sing.image.save(os.path.basename(default_image_path), File(default_image_file))

        # Debug 출력
        print(f"Title: {sing.title}, Artist: {', '.join([artist.title for artist in artists])}")

# 파일 경로 설정
file_path = 'singapp/mydata/songs_modified2.csv'  # 본인의 데이터 파일 경로로 변경
import_data_to_sings(file_path)
