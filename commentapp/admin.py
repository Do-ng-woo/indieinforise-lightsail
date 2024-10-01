from django.contrib import admin

from commentapp.models import Comment, Like
# Register your models here.

admin.site.register(Comment)
admin.site.register(Like)
