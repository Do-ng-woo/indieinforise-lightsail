from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from projectapp.models import Project, Subtitle

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

class HiddenFilter(admin.SimpleListFilter):
    title = _('Hidden status')
    parameter_name = 'hidden'

    def lookups(self, request, model_admin):
        return (
            ('hidden', _('Hidden')),
            ('not_hidden', _('Not Hidden')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'hidden':
            return queryset.filter(hide=True)
        if self.value() == 'not_hidden':
            return queryset.filter(hide=False)

class ProjectAdmin(admin.ModelAdmin):
    actions = ['make_hidden', 'make_not_hidden']
    list_filter = (OrderByFilter, HiddenFilter,)  # Add custom filters

    def make_hidden(self, request, queryset):
        queryset.update(hide=True)
    make_hidden.short_description = "Mark selected projects as hidden"

    def make_not_hidden(self, request, queryset):
        queryset.update(hide=False)
    make_not_hidden.short_description = "Mark selected projects as not hidden"

admin.site.register(Project, ProjectAdmin)

class SubtitleAdmin(admin.ModelAdmin):
    actions = ['delete_selected_subtitles', 'delete_orphan_subtitles']
    list_per_page = 1000  # 한 페이지에 1000개씩 표시
    actions_on_top = True
    actions_on_bottom = True
    list_filter = (HiddenFilter,)

    def delete_selected_subtitles(self, request, queryset):
        queryset.delete()
    delete_selected_subtitles.short_description = "Delete selected subtitles"

    def delete_orphan_subtitles(self, request, queryset):
        # 부모 없는 서브타이틀 필터링 및 삭제
        orphans = Subtitle.objects.filter(project__isnull=True)
        orphans_count = orphans.count()
        orphans.delete()
        self.message_user(request, f"Deleted {orphans_count} orphan subtitles.")
    delete_orphan_subtitles.short_description = "Delete orphan subtitles"

admin.site.register(Subtitle, SubtitleAdmin)