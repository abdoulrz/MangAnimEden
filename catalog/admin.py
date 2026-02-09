from django.contrib import admin
# Trigger reload - Final Fix
from .models import Series, Chapter, Page, Genre


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


from .series_forms import SeriesAdminForm
from .utils import extract_chapter_number
from .services import FileProcessor
from django.core.files.base import ContentFile
from django.contrib import messages

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    """
    Configuration admin pour les séries.
    """
    form = SeriesAdminForm
    fieldsets = (
        ('Informations Générales', {
            'fields': ('title', 'slug', 'type', 'description', 'status', 'release_date')
        }),
        ('Auteurs & Artistes', {
            'fields': ('author', 'artist')
        }),
        ('Médias', {
            'fields': ('cover', 'folder_upload')
        }),
        ('Classification', {
            'fields': ('genres',)
        }),
    )
    list_display = ['title', 'type', 'author', 'status', 'updated_at']
    list_filter = ['type', 'status', 'genres', 'created_at']
    search_fields = ['title', 'author', 'artist', 'type']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    filter_horizontal = ['genres']
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        files = request.FILES.getlist('folder_upload')
        if files:
            processed_count = 0
            processor = FileProcessor()
            
            for f in files:
                chapter_num = extract_chapter_number(f.name)
                if chapter_num is not None:
                    # Create chapter
                    chapter, created = Chapter.objects.get_or_create(
                        series=obj,
                        number=chapter_num,
                        defaults={'title': f"Chapitre {chapter_num}"}
                    )
                    
                    # Save file to chapter
                    chapter.source_file.save(f.name, f, save=True)
                    
                    # Process file
                    if processor.process_chapter(chapter):
                        processed_count += 1
            
            if processed_count > 0:
                messages.success(request, f"{processed_count} chapitres ont été importés et traités avec succès.")
            else:
                messages.warning(request, "Aucun chapitre n'a pu être traité correctement.")


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
