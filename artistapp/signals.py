from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F
from commentapp.models import Comment
from artistapp.models import Artist
from django.db import transaction

import re
from artistapp.models import Subtitle
from hangul_romanize import Transliter
from hangul_romanize.rule import academic
from googletrans import Translator


    
@receiver(post_save, sender=Comment)
def increase_comment_count(sender, instance, created, **kwargs):
    if created:
        # Comment가 ArtistComment 모델에 연결되어 있는지 확인
        content_type = ContentType.objects.get_for_model(Artist)
        if instance.content_type == content_type:
            # ContentType이 Artist, 댓글 수를 증가시킴
            Artist.objects.filter(pk=instance.object_id).update(comment_count=F('comment_count') + 1)

@receiver(post_delete, sender=Comment)
def decrease_comment_count(sender, instance, **kwargs):
    # Comment가 Artist 모델에 연결되어 있는지 확인
    content_type = ContentType.objects.get_for_model(Artist)
    if instance.content_type == content_type:
        # ContentType이 Artist, 댓글 수를 감소시킴
        Artist.objects.filter(pk=instance.object_id).update(comment_count=F('comment_count') - 1)
        
@receiver(post_save, sender=Artist)
def update_post_count_on_save(sender, instance, created, **kwargs):
    if created:
        def _update_post_count():
            if instance.writer:  # writer가 None인 경우를 방지
                user = instance.writer
                user.post_count += 1
                user.save()
        
        transaction.on_commit(_update_post_count)  # 트랜잭션이 커밋된 후 _update_post_count 함수 실행

@receiver(post_delete, sender=Artist)
def update_post_count_on_delete(sender, instance, **kwargs):
    def _decrement_post_count():
        if instance.writer:  # writer가 None인 경우를 방지
            user = instance.writer
            user.post_count = max(0, user.post_count - 1)
            user.save()
    
    transaction.on_commit(_decrement_post_count)  # 트랜잭션이 커밋된 후 _decrement_post_count 함수 실행

# 한글을 영어로 번역하는 함수
def korean_to_english(korean_text):
    translator = Translator()
    translated = translator.translate(korean_text, src='ko', dest='en')
    return translated.text

def generate_subtitles(title):
    subtitles = set()
    if re.search('[가-힣]', title):  # 한글이 포함된 경우
        subtitles.add(title)  # 원본
        subtitles.add(title.replace(" ", ""))  # 띄어쓰기 제거
        english_title = korean_to_english(title)
        subtitles.add(english_title)  # 원본 번역
        subtitles.add(korean_to_english(title.replace(" ", "")))  # 띄어쓰기 제거 후 번역
    else:  # 영어인 경우
        subtitles.add(title.lower())  # 소문자로 변환하여 저장
        if " " in title:
            subtitles.add(title.replace(" ", "").lower())  # 띄어쓰기 제거 후 소문자로 변환
            subtitles.add(title.lower())  # 띄어쓰기가 있는 원본 소문자 추가
    print("Generated subtitles: ", subtitles)  # 디버깅 출력
    return subtitles

@receiver(post_save, sender=Artist)
def create_subtitles_for_artist(sender, instance, created, **kwargs):
    if created:
        subtitles = generate_subtitles(instance.title)
        subtitle_objects = []
        for subtitle_name in subtitles:
            subtitle, _ = Subtitle.objects.get_or_create(name=subtitle_name.lower())  # 소문자로 변환하여 저장
            subtitle_objects.append(subtitle)
            print(f"Subtitle: {subtitle.name}, Created: {created}")  # 디버깅 출력
        instance.sub_titles.set(subtitle_objects)
        instance.save()  # 최종적으로 아티스트 저장
        