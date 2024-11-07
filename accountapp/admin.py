from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, EmailUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('image','gender', 'birth_date', 'nickname', 'purpose_of_use', 'message', 'level', 'points', 'post_count', 'comment_count','performance_points','privacy_policy_agreement','signup_method')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('image','gender', 'birth_date', 'nickname', 'purpose_of_use', 'message', 'level', 'points', 'post_count', 'comment_count','performance_points','privacy_policy_agreement','signup_method')}),
    )

# EmailUser 모델을 Admin에 추가
class EmailUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_verified', 'account_created', 'created_at')
    search_fields = ('email',)
    list_filter = ('is_verified', 'account_created', 'created_at')
    readonly_fields = ('created_at',)  # created_at 필드를 읽기 전용으로 설정

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(EmailUser, EmailUserAdmin)