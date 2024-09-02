from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from artistapp.models import Artist, Subtitle, Description, HonoraryEntry

class OrderByFilter(admin.SimpleListFilter):
    title = _('Order by')
    parameter_name = 'order_by'

    def lookups(self, request, model_admin):
        return (
            ('title_asc', _('Title (A-Z)')),
            ('title_desc', _('Title (Z-A)')),
            ('oldest', _('Oldest')),
            ('newest', _('Newest')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'title_asc':
            return queryset.order_by('title')
        if self.value() == 'title_desc':
            return queryset.order_by('-title')
        if self.value() == 'oldest':
            return queryset.order_by('created_at')
        if self.value() == 'newest':
            return queryset.order_by('-created_at')
        return queryset

class ArtistAdmin(admin.ModelAdmin):
    actions = ['make_hidden', 'make_not_hidden']
    list_per_page = 1000  # 한 페이지에 1000개씩 표시
    list_filter = (OrderByFilter,)  # Add custom filters

    def make_hidden(self, request, queryset):
        queryset.update(hide=True)
    make_hidden.short_description = "Mark selected artists as hidden"

    def make_not_hidden(self, request, queryset):
        queryset.update(hide=False)
    make_not_hidden.short_description = "Mark selected artists as not hidden"

admin.site.register(Artist, ArtistAdmin)

class SubtitleAdmin(admin.ModelAdmin):
    actions = ['delete_selected_subtitles', 'delete_orphan_subtitles']
    list_per_page = 1000  # 한 페이지에 1000개씩 표시
    actions_on_top = True
    actions_on_bottom = True

    def delete_selected_subtitles(self, request, queryset):
        queryset.delete()
    delete_selected_subtitles.short_description = "Delete selected subtitles"

    def delete_orphan_subtitles(self, request, queryset):
        # 부모 없는 서브타이틀 필터링 및 삭제
        orphans = Subtitle.objects.filter(artists__isnull=True)
        orphans_count = orphans.count()
        orphans.delete()
        self.message_user(request, f"Deleted {orphans_count} orphan subtitles.")
    delete_orphan_subtitles.short_description = "Delete orphan subtitles"

admin.site.register(Subtitle, SubtitleAdmin)

class DescriptionAdmin(admin.ModelAdmin):
    actions = ['delete_selected_description']

    def delete_selected_description(self, request, queryset):
        queryset.delete()
    delete_selected_description.short_description = "Delete selected description"

admin.site.register(Description, DescriptionAdmin)


class HonoraryEntryAdmin(admin.ModelAdmin):
    list_display = ('artist', 'year', 'quarter', 'hot_point', 'rank', 'category', 'frame_style')
    list_filter = ('year', 'quarter', 'category')
    search_fields = ('artist__title',)

admin.site.register(HonoraryEntry, HonoraryEntryAdmin)