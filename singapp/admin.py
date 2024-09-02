from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from singapp.models import Sing, Subtitle

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

class SingAdmin(admin.ModelAdmin):
    actions = ['make_hidden', 'make_not_hidden']
    list_filter = (OrderByFilter,)  # Add custom filters

    def make_hidden(self, request, queryset):
        queryset.update(hide=True)
    make_hidden.short_description = "Mark selected sings as hidden"

    def make_not_hidden(self, request, queryset):
        queryset.update(hide=False)
    make_not_hidden.short_description = "Mark selected sings as not hidden"

admin.site.register(Sing, SingAdmin)

class SubtitleAdmin(admin.ModelAdmin):
    actions = ['delete_selected_subtitles']

    def delete_selected_subtitles(self, request, queryset):
        queryset.delete()
    delete_selected_subtitles.short_description = "Delete selected subtitles"

admin.site.register(Subtitle, SubtitleAdmin)
