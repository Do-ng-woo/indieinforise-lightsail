from django.apps import AppConfig


class AlbumappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'albumapp'
    
    def ready(self):
        # 시그널을 여기에서 임포트합니다. 댓글 카운트를 위함
        from . import signals