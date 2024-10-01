from django.apps import AppConfig


class ArticleappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'articleapp'

    def ready(self):
        # 시그널을 여기에서 임포트합니다.
        from . import signals