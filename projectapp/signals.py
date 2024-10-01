from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F
from commentapp.models import Comment
from projectapp.models import Project, Subtitle
from django.db import transaction
import re
from googletrans import Translator

@receiver(post_save, sender=Comment)
def increase_comment_count(sender, instance, created, **kwargs):
    if created:
        # Comment가 Project 모델에 연결되어 있는지 확인
        content_type = ContentType.objects.get_for_model(Project)
        if instance.content_type == content_type:
            # ContentType이 Project, 댓글 수를 증가시킴
            Project.objects.filter(pk=instance.object_id).update(comment_count=F('comment_count') + 1)

@receiver(post_delete, sender=Comment)
def decrease_comment_count(sender, instance, **kwargs):
    # Comment가 Project 모델에 연결되어 있는지 확인
    content_type = ContentType.objects.get_for_model(Project)
    if instance.content_type == content_type:
        # ContentType이 Project, 댓글 수를 감소시킴
        Project.objects.filter(pk=instance.object_id).update(comment_count=F('comment_count') - 1)

        
# 여기에 신호 리시버 함수를 작성합니다.
@receiver(post_save, sender=Project)
def update_post_count_on_save(sender, instance, created, **kwargs):
    if created:
        def _update_post_count():
            if instance.writer:  # writer가 None인 경우를 방지
                user = instance.writer
                user.post_count += 1
                user.save()
        
        transaction.on_commit(_update_post_count)  # 트랜잭션이 커밋된 후 _update_post_count 함수 실행

@receiver(post_delete, sender=Project)
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

# 프로젝트의 제목을 기반으로 부제목 생성 함수
def generate_subtitles(title):
    subtitles = set()
    if re.search('[가-힣]', title):  # 한글이 포함된 경우
        subtitles.add(title)  # 원본 제목
        subtitles.add(title.replace(" ", ""))  # 띄어쓰기 제거된 제목
        english_title = korean_to_english(title)
        subtitles.add(english_title)  # 원본 번역
        subtitles.add(korean_to_english(title.replace(" ", "")))  # 띄어쓰기 제거 후 번역
    else:  # 영어일 경우
        subtitles.add(title.lower())  # 소문자로 변환하여 저장
        if " " in title:
            subtitles.add(title.replace(" ", "").lower())  # 띄어쓰기 제거 후 소문자 변환
            subtitles.add(title.lower())  # 원본 소문자 저장
    print("Generated subtitles: ", subtitles)  # 디버깅용 출력
    return subtitles

# 프로젝트 생성 후 자동으로 부제목을 생성하는 시그널
@receiver(post_save, sender=Project)
def create_subtitles_for_project(sender, instance, created, **kwargs):
    if created:
        subtitles = generate_subtitles(instance.title)
        subtitle_objects = []
        for subtitle_name in subtitles:
            subtitle, _ = Subtitle.objects.get_or_create(name=subtitle_name.lower())  # 소문자로 저장
            subtitle_objects.append(subtitle)
            print(f"Subtitle: {subtitle.name}, Created: {created}")  # 디버깅용 출력
        instance.sub_titles.set(subtitle_objects)  # 생성된 부제목을 프로젝트에 추가
        instance.save()  # 최종적으로 프로젝트 저장