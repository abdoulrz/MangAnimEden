import os
import django
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import sys

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def test_s3():
    print("Testing connection to S3/Cloudflare R2...")
    try:
        # Create a simple test file
        content = b'Hello from MangaAnimEden! S3 storage is working correctly.'
        file_name = 'test_r2_upload.txt'
        
        # Save to default storage (which is now S3Boto3Storage)
        saved_path = default_storage.save(file_name, ContentFile(content))
        
        print(f"✅ Success! File uploaded as: {saved_path}")
        
        # Get the URL (This checks if AWS_S3_CUSTOM_DOMAIN / AWS_S3_ENDPOINT_URL is working)
        file_url = default_storage.url(saved_path)
        print(f"✅ File URL: {file_url}")
        
        # Optional: Clean up the test file
        default_storage.delete(saved_path)
        print(f"✅ Test file deleted.")
        print("Everything is perfectly configured!")
        
    except Exception as e:
        print(f"❌ Upload failed!")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    test_s3()
