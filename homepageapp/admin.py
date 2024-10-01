from django.contrib import admin
from homepageapp.models import Homepage



# Homepage 모델을 위한 Admin 클래스를 정의합니다.
class HomepageAdmin(admin.ModelAdmin):
    # 관리자 페이지에서 표시할 필드를 지정합니다.
    list_display = ('id', 'writer')

# 관리자 페이지에 Homepage 모델을 등록합니다.
admin.site.register(Homepage, HomepageAdmin)
