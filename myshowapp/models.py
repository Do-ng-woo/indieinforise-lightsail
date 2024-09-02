from django.db import models
from articleapp.models import Article
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from myshowapp.utils import create_stamp_image

class Stamp(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='stamps')
    full_text = models.TextField()
    first_line = models.TextField()
    second_line = models.TextField(null=True, blank=True)
    third_line = models.TextField(null=True, blank=True)
    date = models.DateField()
    font_choice = models.IntegerField(choices=[(i, f'Font {i}') for i in range(1, 7)])
    background_choice = models.IntegerField(choices=[(i, f'Background {i}') for i in range(1, 4)])
    center_image_choice = models.IntegerField(choices=[(i, f'Center Image {i}') for i in range(1, 5)])
    color_choice = models.CharField(max_length=10, choices=[('blue', 'Blue'), ('yellow', 'Yellow'), ('red', 'Red'), ('black', 'Black')])

    def __str__(self):
        return f'Stamp for {self.article.title}'

class UserPerformance(models.Model):
    STATUS_CHOICES = (
        ('W', 'Will Watch'),
        ('S', 'Saw'),
        ('L', 'Like')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performances')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='user_performances')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    
    rating = models.PositiveIntegerField()  # 별점 필드 추가 (필수)
    memo = models.TextField(null=True, blank=True)  # 메모 필드 추가 (선택)
    running_time = models.IntegerField(null=True, blank=True)  # 러닝타임 필드 추가 (선택, 단위: 분)
    stamp_image = models.ImageField(upload_to='stamps/', null=True, blank=True)  # 스탬프 이미지 필드 추가
    stamp = models.OneToOneField(Stamp, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.user} - {self.article} - {self.status}'

@receiver(post_save, sender=Stamp)
def update_stamp_image(sender, instance, **kwargs):
    try:
        user_performance = UserPerformance.objects.get(stamp=instance)
        user_performance.stamp_image = create_stamp_image(instance)
        user_performance.save()
    except UserPerformance.DoesNotExist:
        pass

@receiver(post_delete, sender=UserPerformance)
def delete_stamp_on_user_performance_delete(sender, instance, **kwargs):
    try:
        if instance.stamp:
            instance.stamp.delete()
    except Stamp.DoesNotExist:
        pass
    
# ======================================================일러스트부분 시작=============================================================================================

from django.db import models
from django.conf import settings

class Background_illust(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='backgrounds/')

    def __str__(self):
        return self.name

class Singer_illust(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='singers/')

    def __str__(self):
        return self.name

class Guitarist_illust(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='guitarists/')

    def __str__(self):
        return self.name

class Bassist_illust(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='bassists/')

    def __str__(self):
        return self.name

class Drummer_illust(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='drummers/')

    def __str__(self):
        return self.name

class Keyboardist_illust(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='keyboardists/')

    def __str__(self):
        return self.name

class Audience_illust(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='audiences/')

    def __str__(self):
        return self.name

class Lighting_illust(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='lightings/')

    def __str__(self):
        return self.name

class MyShow_illust(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='myshows')
    background = models.ForeignKey(Background_illust, on_delete=models.SET_NULL, null=True, blank=True)
    singer = models.ForeignKey(Singer_illust, on_delete=models.SET_NULL, null=True, blank=True)
    guitarist = models.ForeignKey(Guitarist_illust, on_delete=models.SET_NULL, null=True, blank=True)
    bassist = models.ForeignKey(Bassist_illust, on_delete=models.SET_NULL, null=True, blank=True)
    drummer = models.ForeignKey(Drummer_illust, on_delete=models.SET_NULL, null=True, blank=True)
    keyboardist = models.ForeignKey(Keyboardist_illust, on_delete=models.SET_NULL, null=True, blank=True)
    audience = models.ForeignKey(Audience_illust, on_delete=models.SET_NULL, null=True, blank=True)
    lighting = models.ForeignKey(Lighting_illust, on_delete=models.SET_NULL, null=True, blank=True)
    positions = models.TextField(null=True, blank=True)  # JSON으로 위치 정보 저장
    sizes = models.TextField(null=True, blank=True)  # JSON으로 위치 정보 저장
    z_indices = models.TextField(null=True, blank=True)  # JSON으로 z-index 정보 저장

    def __str__(self):
        return f'{self.user} - My Show'
