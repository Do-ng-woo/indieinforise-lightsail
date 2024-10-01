from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('image','gender', 'birth_date', 'nickname', 'purpose_of_use', 'message', 'level', 'points', 'post_count', 'comment_count','performance_points','privacy_policy_agreement')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('image','gender', 'birth_date', 'nickname', 'purpose_of_use', 'message', 'level', 'points', 'post_count', 'comment_count','performance_points','privacy_policy_agreement')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)