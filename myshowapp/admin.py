from django.contrib import admin
from .models import UserPerformance, Stamp

class StampAdmin(admin.ModelAdmin):
    list_display = ('article', 'full_text', 'first_line', 'second_line', 'third_line', 'date', 'font_choice', 'background_choice', 'center_image_choice', 'color_choice')
    search_fields = ('article__title', 'full_text', 'first_line', 'second_line', 'third_line')

admin.site.register(Stamp, StampAdmin)

class UserPerformanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'status', 'rating', 'running_time', 'get_stamp_full_text', 'get_stamp_date', 'get_stamp_font_choice', 'get_stamp_background_choice', 'get_stamp_center_image_choice', 'get_stamp_color_choice')
    search_fields = ('user__username', 'article__title', 'status', 'stamp__full_text')

    def get_stamp_full_text(self, obj):
        return obj.stamp.full_text if obj.stamp else None
    get_stamp_full_text.short_description = 'Stamp Full Text'

    def get_stamp_date(self, obj):
        return obj.stamp.date if obj.stamp else None
    get_stamp_date.short_description = 'Stamp Date'

    def get_stamp_font_choice(self, obj):
        return obj.stamp.font_choice if obj.stamp else None
    get_stamp_font_choice.short_description = 'Stamp Font Choice'

    def get_stamp_background_choice(self, obj):
        return obj.stamp.background_choice if obj.stamp else None
    get_stamp_background_choice.short_description = 'Stamp Background Choice'

    def get_stamp_center_image_choice(self, obj):
        return obj.stamp.center_image_choice if obj.stamp else None
    get_stamp_center_image_choice.short_description = 'Stamp Center Image Choice'

    def get_stamp_color_choice(self, obj):
        return obj.stamp.color_choice if obj.stamp else None
    get_stamp_color_choice.short_description = 'Stamp Color Choice'

admin.site.register(UserPerformance, UserPerformanceAdmin)



from .models import Background_illust, Singer_illust, Guitarist_illust, Bassist_illust, Drummer_illust, Keyboardist_illust, Audience_illust, Lighting_illust, MyShow_illust

@admin.register(Background_illust)
class BackgroundIllustAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']
    search_fields = ['name']

@admin.register(Singer_illust)
class SingerIllustAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']
    search_fields = ['name']

@admin.register(Guitarist_illust)
class GuitaristIllustAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']
    search_fields = ['name']

@admin.register(Bassist_illust)
class BassistIllustAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']
    search_fields = ['name']

@admin.register(Drummer_illust)
class DrummerIllustAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']
    search_fields = ['name']

@admin.register(Keyboardist_illust)
class KeyboardistIllustAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']
    search_fields = ['name']

@admin.register(Audience_illust)
class AudienceIllustAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']
    search_fields = ['name']

@admin.register(Lighting_illust)
class LightingIllustAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']
    search_fields = ['name']
    
@admin.register(MyShow_illust)
class MyShowIllustAdmin(admin.ModelAdmin):
    list_display = ['user', 'background', 'singer', 'guitarist', 'bassist', 'drummer', 'keyboardist', 'audience', 'lighting']
    search_fields = ['user__username']
    raw_id_fields = ['user', 'background', 'singer', 'guitarist', 'bassist', 'drummer', 'keyboardist', 'audience', 'lighting']