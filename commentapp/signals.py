from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from commentapp.models import Comment  
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=Comment)
def update_comment_count_on_save(sender, instance, created, **kwargs):
    if created:
        user = instance.writer
        user.comment_count += 1
        user.save()

@receiver(post_delete, sender=Comment)
def update_comment_count_on_delete(sender, instance, **kwargs):
    user = instance.writer
    user.comment_count = max(0, user.comment_count - 1)
    user.save()