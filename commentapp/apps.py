from django.apps import AppConfig


class CommentappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'commentapp'
    
    def ready(self):
        
        from . import signals