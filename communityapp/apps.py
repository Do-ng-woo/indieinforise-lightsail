from django.apps import AppConfig


class CommunityappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'communityapp'
    
    def ready(self):
        # 시그널을 여기에서 임포트합니다.
        from . import signals
    