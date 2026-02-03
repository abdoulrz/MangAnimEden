import os
import sys
import django
from django.core.files import File
from django.conf import settings

# Setup Django environment
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Series, Chapter, Page

def populate():
    # 1. Create Series
    series, created = Series.objects.get_or_create(
        title="MangAnimEDen Demo",
        defaults={
            'description': "Une série de démonstration pour tester le lecteur.",
            'author': "Antigravity",
            'artist': "DeepMind",
            'status': "completed"
        }
    )
    if created:
        print(f"Created Series: {series}")
    else:
        print(f"Found Series: {series}")

    # 2. Create Chapter
    chapter, created = Chapter.objects.get_or_create(
        series=series,
        number=1,
        defaults={
            'title': "Le Commencement"
        }
    )
    if created:
        print(f"Created Chapter: {chapter}")
    else:
        print(f"Found Chapter: {chapter}")

    # 3. Create Page
    # Path to the image we copied
    image_path = os.path.join(settings.MEDIA_ROOT, 'mangas', 'demo_page.png')
    
    if os.path.exists(image_path):
        # We check if pages exist to avoid duplicates if run multiple times
        if not Page.objects.filter(chapter=chapter, page_number=1).exists():
            page = Page(
                chapter=chapter,
                page_number=1
            )
            # We need to open the file to save it to the ImageField
            # However, since the file is already in media, we might duplicate it if we use save()
            # But specific path assignment is tricky with ImageField if we don't want to move it.
            # Let's just point to it properly.
            
            # Simple approach: Assign the relative path to the field.
            # This assumes the file is where we put it relative to MEDIA_ROOT.
            page.image.name = 'mangas/demo_page.png' 
            page.save()
            print(f"Created Page 1 for {chapter}")
        else:
            print("Page 1 already exists.")
    else:
        print(f"Error: Image not found at {image_path}")

if __name__ == '__main__':
    populate()
