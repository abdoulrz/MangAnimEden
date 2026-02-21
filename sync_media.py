import os
import django
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pathlib import Path

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def sync_local_media_to_r2():
    local_media_dir = Path(settings.BASE_DIR) / 'media'
    
    if not local_media_dir.exists():
        print(f"Directory {local_media_dir} does not exist. Nothing to sync.")
        return

    print(f"Scanning local media directory: {local_media_dir}")
    
    # Loop through all files in the local media directory
    for root, dirs, files in os.walk(local_media_dir):
        for file in files:
            local_path = Path(root) / file
            
            # Create the relative path (e.g., 'avatars/my_avatar.png')
            relative_path = str(local_path.relative_to(local_media_dir)).replace('\\', '/')
            
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
