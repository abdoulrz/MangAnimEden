import os
import re
import django
from django.conf import settings

# Setup Django environment
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Series, Chapter

def import_the_boxer():
    # 1. Create Series
    series, created = Series.objects.get_or_create(
        title="The Boxer",
        defaults={
            'description': "You have raw talent. Or I should say, you're a monster.",
            'author': "JH",
            'artist': "JH",
            'status': "completed",
            'slug': 'the-boxer'
        }
    )
    if created:
        print(f"Created Series: {series}")
    else:
        print(f"Found Series: {series}")

    # 2. Scan Directory
    manga_dir = os.path.join(settings.MEDIA_ROOT, 'mangas', 'The boxer')
    if not os.path.exists(manga_dir):
        print(f"Directory not found: {manga_dir}")
        return

    files = sorted(os.listdir(manga_dir))
    
    # Regex to extract chapter number
    # Matches "Chapter 01", "Chapter 101", "Chapter 51.5"
    pattern = re.compile(r'Chapter\s+(\d+(?:\.\d+)?)')

    for filename in files:
        if not filename.endswith('.pdf'):
            continue
            
        match = pattern.search(filename)
        if match:
            chapter_num = float(match.group(1))
            
            # Create Chapter
            chapter, created = Chapter.objects.get_or_create(
                series=series,
                number=chapter_num,
                defaults={
                    'title': f"Chapter {chapter_num}"
                }
            )
            
            # Assign PDF file
            # Path relative to MEDIA_ROOT
            relative_path = os.path.join('mangas', 'The boxer', filename).replace('\\', '/')
            
            # Only update if not set or different (to be safe, just update if created or force update)
            if created or not chapter.pdf_file:
                chapter.pdf_file.name = relative_path
                chapter.save()
                print(f"Imported Chapter {chapter_num} from {filename}")
            else:
                print(f"Chapter {chapter_num} already exists (skipping file update).")
        else:
            print(f"Could not parse chapter number from: {filename}")

if __name__ == '__main__':
    import_the_boxer()
