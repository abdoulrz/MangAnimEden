from django.contrib import admin
from .models import ReadingProgress


@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    """
    Configuration admin pour la progression de lecture.
    """
    list_display = ['user', 'chapter', 'current_page', 'completed', 'last_read']
    list_filter = ['completed', 'last_read']
    search_fields = ['user__nickname', 'chapter__series__title']
    ordering = ['-last_read']
