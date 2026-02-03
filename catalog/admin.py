from django.contrib import admin
from .models import Series, Chapter, Page


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    """
    Configuration admin pour les séries.
    """
    list_display = ['title', 'author', 'status', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'author', 'artist']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    """
    Configuration admin pour les chapitres.
    """
    list_display = ['series', 'number', 'title', 'created_at']
    list_filter = ['series', 'created_at']
    search_fields = ['series__title', 'title']
    ordering = ['-created_at']


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """
    Configuration admin pour les pages.
    """
    list_display = ['chapter', 'page_number', 'created_at']
    list_filter = ['chapter__series', 'created_at']
    search_fields = ['chapter__series__title']
    ordering = ['chapter', 'page_number']
