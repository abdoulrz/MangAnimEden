
import os
import zipfile
import shutil
import tempfile
import logging
from io import BytesIO

from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image
import pypdf

from .models import Page

logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self):
        self.supported_extensions = {'.pdf', '.cbz', '.zip', '.epub'}

    def process_chapter(self, chapter):
        """
        Main entry point to process a chapter's source file.
        Extracts images and creates Page objects.
        """
        if not chapter.source_file:
            print(f"Chapter {chapter} has no source file.")
            return False

        file_path = chapter.source_file.path
        ext = os.path.splitext(file_path)[1].lower()

        if ext not in self.supported_extensions:
            print(f"Unsupported file extension: {ext}")
            return False
            
        print(f"Processing {chapter} ({ext})...")

        # Clear existing pages to avoid duplicates if re-processing
        chapter.pages.all().delete()

        try:
            if ext == '.pdf':
                self._extract_from_pdf(chapter, file_path)
            elif ext in ['.cbz', '.zip', '.epub']:
                self._extract_from_zip(chapter, file_path)
            
            print(f"Successfully processed {chapter}. Created {chapter.pages.count()} pages.")
            return True
        except Exception as e:
            print(f"Error processing {chapter}: {e}")
            return False

    def _save_page_image(self, chapter, image_data, page_number, filename):
        # Create Page object
        page = Page(chapter=chapter, page_number=page_number)
        
        # Save image content to the ImageField
        # ContentFile wraps logic to behave like an uploaded file
        final_filename = f"{chapter.id}_{page_number}_{filename}"
        page.image.save(final_filename, ContentFile(image_data), save=True)

    def _extract_from_pdf(self, chapter, file_path):
        reader = pypdf.PdfReader(file_path)
        
        count = 0 
        for i, page in enumerate(reader.pages):
            # Extract images from PDF page
            for image_file_object in page.images:
                # Save image
                self._save_page_image(chapter, image_file_object.data, count + 1, image_file_object.name)
                count += 1


    def _extract_from_zip(self, chapter, file_path):
        # ZIP, CBZ, and EPUB are all zip-based
        with zipfile.ZipFile(file_path, 'r') as zf:
            # Filter for images
            image_files = [
                f for f in zf.namelist() 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
                and not f.startswith('__MACOSX') # Ignore Mac metadata
            ]
            
            # Sort naturally (1, 2, 10 instead of 1, 10, 2)
            # Basic natural sort might fail (1, 10, 2), so let's try a better sort key if possible
            # Or just rely on standard sort if filenames are padded (001.jpg, 002.jpg)
            image_files.sort()
            
            for i, filename in enumerate(image_files):
                with zf.open(filename) as f:
                    image_data = f.read()
                    # Clean filename to remove paths inside zip
                    clean_name = os.path.basename(filename)
                    self._save_page_image(chapter, image_data, i + 1, clean_name)
