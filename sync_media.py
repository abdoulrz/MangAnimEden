import os
import django
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pathlib import Path
from decouple import config

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def sync_local_media_to_r2():
    # Because there was no MEDIA_ROOT originally, files like 'scans/82.cbz' ended up in the project root
    media_dirs_to_sync = ['scans', 'stories', 'covers', 'avatars', 'badges', 'Background', 'group_icons', 'temp_uploads']
    base_dir = Path(settings.BASE_DIR)

    for dir_name in media_dirs_to_sync:
        local_dir = base_dir / dir_name
        
        if not local_dir.exists():
            print(f"Skipping {dir_name}/ - does not exist.")
            continue

        print(f"\nScanning directory: {local_dir}")
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_path = Path(root) / file
                
                # We want the path IN the bucket to be e.g. 'scans/file.cbz'
                # So we take the path relative to the base project dir
                relative_path = str(local_path.relative_to(base_dir)).replace('\\', '/')
                
            
            print(f"Uploading {relative_path}...")
            
            try:
                # Read the local file
                with open(local_path, 'rb') as f:
                    content = f.read()
                
                # Check if it already exists to prevent duplicate work (optional but safe)
                if default_storage.exists(relative_path):
                    print(f"  -> File {relative_path} already exists on R2. Skipping.")
                    continue
                
                # Save it to R2
                default_storage.save(relative_path, ContentFile(content))
                print(f"  -> Successfully uploaded {relative_path}!")
                
            except Exception as e:
                print(f"  -> Error uploading {relative_path}: {e}")

if __name__ == '__main__':
    sync_local_media_to_r2()
