from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F
from commentapp.models import Comment
from communityapp.models import Community
from django.db import transaction

@receiver(post_save, sender=Comment)
def increase_comment_count(sender, instance, created, **kwargs):
    if created:
        # Comment가 Article 모델에 연결되어 있는지 확인
        content_type = ContentType.objects.get_for_model(Community)
        if instance.content_type == content_type:
            # ContentType이 Community, 댓글 수를 증가시킴
            Community.objects.filter(pk=instance.object_id).update(comment_count=F('comment_count') + 1)

@receiver(post_delete, sender=Comment)
def decrease_comment_count(sender, instance, **kwargs):
    # Comment가 Community 모델에 연결되어 있는지 확인
    content_type = ContentType.objects.get_for_model(Community)
    if instance.content_type == content_type:
        # ContentType이 Community, 댓글 수를 감소시킴
        Community.objects.filter(pk=instance.object_id).update(comment_count=F('comment_count') - 1)
        
        
@receiver(post_save, sender=Community)
def update_post_count_on_save(sender, instance, created, **kwargs):
    if created:
        def _update_post_count():
            if instance.writer:  # writer가 None인 경우를 방지
                user = instance.writer
                user.post_count += 1
                user.save()
        
        transaction.on_commit(_update_post_count)  # 트랜잭션이 커밋된 후 _update_post_count 함수 실행

@receiver(post_delete, sender=Community)
def update_post_count_on_delete(sender, instance, **kwargs):
    def _decrement_post_count():
        if instance.writer:  # writer가 None인 경우를 방지
            user = instance.writer
            user.post_count = max(0, user.post_count - 1)
            user.save()
    
    transaction.on_commit(_decrement_post_count)  # 트랜잭션이 커밋된 후 _decrement_post_count 함수 실행