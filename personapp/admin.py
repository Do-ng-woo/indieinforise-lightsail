from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from personapp.models import Person, Subtitle

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

class EmptyTitleFilter(admin.SimpleListFilter):
    title = _('Title empty')
    parameter_name = 'title_empty'

    def lookups(self, request, model_admin):
        return (
            ('Yes', _('Yes')),
            ('No', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(title='')
        if self.value() == 'No':
            return queryset.exclude(title='')
        return queryset

class PersonAdmin(admin.ModelAdmin):
    actions = ['make_hidden', 'make_not_hidden']
    list_filter = (OrderByFilter,)  # Add custom filters

    def make_hidden(self, request, queryset):
        queryset.update(hide=True)
    make_hidden.short_description = "Mark selected persons as hidden"

    def make_not_hidden(self, request, queryset):
        queryset.update(hide=False)
    make_not_hidden.short_description = "Mark selected persons as not hidden"

admin.site.register(Person, PersonAdmin)

class SubtitleAdmin(admin.ModelAdmin):
    actions = ['delete_selected_subtitles']
    list_filter = (EmptyTitleFilter,)  # Add custom filters

    def delete_selected_subtitles(self, request, queryset):
        queryset.delete()
    delete_selected_subtitles.short_description = "Delete selected subtitles"

admin.site.register(Subtitle, SubtitleAdmin)
