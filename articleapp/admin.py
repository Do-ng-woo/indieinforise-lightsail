from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from articleapp.models import Article

# Register your models here.
# admin.py
class EmptyImageFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the right admin sidebar just above the filter options.
    title = _('Image empty')
    
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'image_empty'
    
    def lookups(self, request, model_admin):
        # This is where you define the values and their labels for the filter.
        return (
            ('Yes', _('Yes')),
            ('No', _('No')),
        )
    
    def queryset(self, request, queryset):
        # This is where you process the selected filter value and return the filtered queryset.
        if self.value() == 'Yes':
            return queryset.filter(image='')
        if self.value() == 'No':
            return queryset.exclude(image='')


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


class ArticleAdmin(admin.ModelAdmin):
    actions = ['make_hidden', 'make_not_hidden']
    list_per_page = 100  # 한 페이지에 100개씩 표시
    list_filter = (EmptyImageFilter, OrderByFilter, HiddenFilter,)  # Add the custom filters to the list_filter

    def make_hidden(self, request, queryset):
        queryset.update(hide=True)
    make_hidden.short_description = "Mark selected articles as hidden"

    def make_not_hidden(self, request, queryset):
        queryset.update(hide=False)
    make_not_hidden.short_description = "Mark selected articles as not hidden"


admin.site.register(Article, ArticleAdmin)
