from django.apps import AppConfig


class ArtistappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'artistapp'
    
    def ready(self):
        # 시그널을 여기에서 임포트합니다.
        from . import signals
