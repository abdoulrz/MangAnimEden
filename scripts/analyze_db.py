import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Series, Chapter, Page
with open('db_output_utf8.txt', 'w', encoding='utf-8') as f:
    series = Series.objects.filter(title__icontains='boxer').first()
    if not series:
        f.write("Series not found\n")
    else:
        f.write(f"Series: {series.title}\n")
        for chapter in series.chapters.all().order_by('number'):
            f.write(f"Chapter {chapter.number}\n")
            if chapter.source_file:
                f.write(f"  Source file: {chapter.source_file.name}\n")
            pages = chapter.pages.all()
            f.write(f"  Pages count: {pages.count()}\n")
            if pages.exists():
                f.write(f"  First 3 pages: {[p.image.name for p in pages[:3]]}\n")
