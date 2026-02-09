import os
import sys
import django
from django.conf import settings

# Add project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Chapter

def inspect_chapters():
    print("Inspecting Chapter file paths...")
    chapters_with_files = Chapter.objects.exclude(source_file='')
    
    print(f"Found {chapters_with_files.count()} chapters with files linked.")
    
    scans_root = os.path.join(settings.MEDIA_ROOT, 'scans')
    print(f"Checking against Scans Root: {scans_root}")
    
    # Check if scans dir exists
    if not os.path.exists(scans_root):
        print("WARNING: 'scans' directory does not exist in MEDIA_ROOT!")
        # return
    
    for chapter in chapters_with_files[:20]:  # Inspect first 20
        print(f"\nChapter: {chapter.series.title} #{chapter.number}")
        try:
            current_name = chapter.source_file.name
            print(f"  DB Value: {current_name}")
            
            try:
                current_path = chapter.source_file.path
                print(f"  Full Path: {current_path}")
                print(f"  Exists at current path? {os.path.exists(current_path)}")
            except ValueError:
                print("  Full Path: <Cannot resolve path - file might be missing>")
                current_path = None

            # Check if it exists in scans/ with the basename
            if current_name:
                basename = os.path.basename(current_name)
                potential_new_path = os.path.join(scans_root, basename)
                print(f"  Checking new path: {potential_new_path}")
                print(f"  Exists at new path? {os.path.exists(potential_new_path)}")
        except Exception as e:
            print(f"  Error accessing file info: {e}")

if __name__ == '__main__':
    inspect_chapters()
