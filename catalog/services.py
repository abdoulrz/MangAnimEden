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

try:
    import rarfile
    # Configure rarfile to find UnRAR.exe on Windows
    import platform
    if platform.system() == 'Windows':
        _unrar_paths = [
            r'C:\Program Files\WinRAR\UnRAR.exe',
            r'C:\Program Files (x86)\WinRAR\UnRAR.exe',
        ]
        for _p in _unrar_paths:
            if os.path.exists(_p):
                rarfile.UNRAR_TOOL = _p
                break
    HAS_RARFILE = True
except ImportError:
    HAS_RARFILE = False

from .models import Page, Chapter, Series
from .utils import extract_chapter_number

logger = logging.getLogger(__name__)

def process_single_chapter_from_temp(series_id, temp_file_path):
    """
    Processes a single chapter file from temp_uploads and links it to a series.
    Returns the Chapter object.
    """
    series = Series.objects.get(id=series_id)
    filename = os.path.basename(temp_file_path)
    chapter_num = extract_chapter_number(filename)
    
    if chapter_num is None:
        raise ValueError(f"Impossible d'extraire le numéro de chapitre du fichier : {filename}")

    # Create chapter
    chapter, created = Chapter.objects.get_or_create(
        series=series,
        number=chapter_num,
        defaults={'title': f"Chapitre {chapter_num}"}
    )
    
    # Save file to chapter FileField
    from django.core.files import File
    with open(temp_file_path, 'rb') as f:
        chapter.source_file.save(filename, File(f), save=True)
    
    # Process file to extract pages
    processor = FileProcessor()
    processor.process_chapter(chapter)
    
    return chapter

def bulk_create_chapters_from_folder(series, files):
    """
    Takes a list of uploaded files (from request.FILES.getlist),
    creates Chapter objects for the given Series, and processes the files.
    Returns count of successfully processed chapters.
    """
    processed_count = 0
    processor = FileProcessor()

    for f in files:
        chapter_num = extract_chapter_number(f.name)
        if chapter_num is not None:
            chapter, created = Chapter.objects.get_or_create(
                series=series,
                number=chapter_num,
                defaults={'title': f"Chapitre {chapter_num}"}
            )
            
            # Save file to chapter
            chapter.source_file.save(f.name, f, save=True)
            
            # Process file
            try:
                if processor.process_chapter(chapter):
                    processed_count += 1
            except Exception as e:
                logger.error(f"Error processing chapter {chapter_num}: {e}")
                
    return processed_count

class FileProcessor:
    def __init__(self):
        self.supported_extensions = {'.pdf', '.cbz', '.cbr', '.zip', '.epub'}

    def process_chapter(self, chapter):
        """
        Main entry point to process a chapter's source file.
        Extracts images and creates Page objects.
        """
        if not chapter.source_file:
            logger.warning(f"Chapter {chapter} has no source file.")
            return False

        file_path = chapter.source_file.path
        ext = os.path.splitext(file_path)[1].lower()

        if ext not in self.supported_extensions:
            logger.warning(f"Unsupported file extension: {ext}")
            return False
            
        logger.info(f"Processing {chapter} ({ext})...")

        try:
            if ext == '.pdf':
                self._extract_from_pdf(chapter, file_path)
            elif ext == '.cbr':
                self._extract_from_rar(chapter, file_path)
            elif ext in ['.cbz', '.zip', '.epub']:
                self._extract_from_zip(chapter, file_path)
            elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
                page_count = chapter.pages.count()
                self._save_page_image(chapter, chapter.source_file.read(), page_count + 1, os.path.basename(file_path))
            
            logger.info(f"Successfully processed {chapter}. Total pages: {chapter.pages.count()}")
            return True
        except Exception as e:
            logger.error(f"Error processing {chapter}: {e}")
            return False

    def _save_page_image(self, chapter, image_data, page_number, filename):
        """Create a Page object and save the image data."""
        page = Page(chapter=chapter, page_number=page_number)
        final_filename = f"{chapter.id}_{page_number}_{filename}"
        page.image.save(final_filename, ContentFile(image_data), save=True)

    def _extract_from_pdf(self, chapter, file_path):
        """Extract images from PDF files."""
        chapter.pages.all().delete()
        
        reader = pypdf.PdfReader(file_path)
        
        count = 0 
        for i, page in enumerate(reader.pages):
            for image_file_object in page.images:
                self._save_page_image(chapter, image_file_object.data, count + 1, image_file_object.name)
                count += 1

    def _extract_from_rar(self, chapter, file_path):
        """Extract images from RAR/CBR archives."""
        if not HAS_RARFILE:
            raise ImportError(
                "Le paquet 'rarfile' est requis pour traiter les fichiers .cbr. "
                "Installez-le avec: pip install rarfile"
            )
        
        chapter.pages.all().delete()
        
        try:
            with rarfile.RarFile(file_path, 'r') as rf:
                image_files = [
                    f for f in rf.namelist()
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
                    and not f.startswith('__MACOSX')
                ]
                
                image_files.sort()
                
                for i, filename in enumerate(image_files):
                    with rf.open(filename) as f:
                        image_data = f.read()
                        clean_name = os.path.basename(filename)
                        self._save_page_image(chapter, image_data, i + 1, clean_name)
        except rarfile.BadRarFile:
            # Some .cbr files are actually ZIP-compressed (mislabeled)
            logger.warning(f"CBR file {file_path} is not a valid RAR, trying as ZIP...")
            self._extract_from_zip(chapter, file_path)

    def _extract_from_zip(self, chapter, file_path):
        """Extract images from ZIP/CBZ/EPUB archives."""
        chapter.pages.all().delete()
        
        with zipfile.ZipFile(file_path, 'r') as zf:
            image_files = [
                f for f in zf.namelist() 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
                and not f.startswith('__MACOSX')
            ]
            
            image_files.sort()
            
            for i, filename in enumerate(image_files):
                with zf.open(filename) as f:
                    image_data = f.read()
                    clean_name = os.path.basename(filename)
                    self._save_page_image(chapter, image_data, i + 1, clean_name)
