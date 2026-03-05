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

# Try to import requests for downloading files if needed
try:
    import requests
except ImportError:
    requests = None

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

def process_single_chapter_from_temp(series_id, temp_file_path, upload_id=None):
    """
    Processes a single chapter file from temp_uploads and links it to a series.
    Returns the Chapter object.
    """
    series = Series.objects.get(id=series_id)
    filename = os.path.basename(temp_file_path)
    chapter_num = extract_chapter_number(filename)
    
    if chapter_num is None:
        raise ValueError(f"Impossible d'extraire le numéro de chapitre du fichier : {filename}")

    # Resolve collisions: if chapter number exists, find the next available decimal (e.g., 1.0 -> 1.1)
    original_chapter_num = chapter_num
    counter = 1
    while True:
        try:
            # Atomic creation to avoid race conditions
            chapter, created = Chapter.objects.get_or_create(
                series=series,
                number=chapter_num,
                defaults={'title': f"Chapitre {chapter_num}"}
            )
            # If we get here, either we created it, or it already existed.
            # If it already existed and we are processing a new upload for it, 
            # we might want to overwrite or create a new one. 
            # Let's assume if it exists, the user might be re-uploading, 
            # so we just use it. But if they uploaded two files in the same batch,
            # this prevents the crash.
            break
        except Exception as e:
            # If there's an IntegrityError (UniqueConstraint), increment and try again
            import django.db.utils
            if isinstance(e, django.db.utils.IntegrityError):
                chapter_num = round(original_chapter_num + (counter * 0.1), 1)
                counter += 1
            else:
                raise

    # Save file to chapter FileField
    from django.core.files import File
    with open(temp_file_path, 'rb') as f:
        chapter.source_file.save(filename, File(f), save=True)
    
    # Process file to extract pages
    processor = FileProcessor(upload_id=upload_id)
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
            original_chapter_num = chapter_num
            counter = 1
            while True:
                try:
                    chapter, created = Chapter.objects.get_or_create(
                        series=series,
                        number=chapter_num,
                        defaults={'title': f"Chapitre {chapter_num}"}
                    )
                    break
                except Exception as e:
                    import django.db.utils
                    if isinstance(e, django.db.utils.IntegrityError):
                        chapter_num = round(original_chapter_num + (counter * 0.1), 1)
                        counter += 1
                    else:
                        raise e
            
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
    def __init__(self, upload_id=None):
        self.supported_extensions = {'.pdf', '.cbz', '.cbr', '.zip', '.epub'}
        self.upload_id = upload_id

    def process_chapter(self, chapter):
        """
        Main entry point to process a chapter's source file.
        Extracts images and creates Page objects.
        """
        if not chapter.source_file:
            logger.warning(f"Chapter {chapter} has no source file.")
            return False

        # Determine extension from the file field name (URL or path)
        ext = os.path.splitext(chapter.source_file.name)[1].lower()

        if ext not in self.supported_extensions:
            logger.warning(f"Unsupported file extension: {ext}")
            return False
            
        logger.info(f"Processing {chapter} ({ext})...")

        # Create a temporary file to work with, verifying safe for cloud storage
        try:
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
                # Write file content to temp file
                # Use chunks to handle large files efficiently
                if hasattr(chapter.source_file, 'open'):
                     chapter.source_file.open('rb')
                
                for chunk in chapter.source_file.chunks():
                    tmp_file.write(chunk)
                
                # Close explicitly to ensure flush
                tmp_file.close()
                temp_path = tmp_file.name

            # Now process using the local temp path
            result = False
            if ext == '.pdf':
                self._extract_from_pdf(chapter, temp_path)
                result = True
            elif ext == '.cbr':
                self._extract_from_rar(chapter, temp_path)
                result = True
            elif ext in ['.cbz', '.zip', '.epub']:
                self._extract_from_zip(chapter, temp_path)
                result = True
            elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
                # If single image, just save it.
                with open(temp_path, 'rb') as f:
                    page_count = chapter.pages.count()
                    self._save_page_image(chapter, f.read(), page_count + 1, os.path.basename(chapter.source_file.name))
                result = True
            
            if result:
                logger.info(f"Successfully processed {chapter}. Total pages: {chapter.pages.count()}")
            return result

        except Exception as e:
            logger.error(f"Error processing {chapter}: {e}")
            return False
        finally:
            # Clean up temporary file
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError as e:
                    logger.warning(f"Failed to delete temp file {temp_path}: {e}")

    def _process_from_path(self, chapter, file_path):
        """Process a chapter directly from a local file path (no R2 download needed)."""
        ext = os.path.splitext(file_path)[1].lower()

        if ext not in self.supported_extensions:
            logger.warning(f"Unsupported file extension: {ext}")
            return False

        logger.info(f"Processing {chapter} from local path ({ext})...")

        try:
            if ext == '.pdf':
                self._extract_from_pdf(chapter, file_path)
            elif ext == '.cbr':
                self._extract_from_rar(chapter, file_path)
            elif ext in ['.cbz', '.zip', '.epub']:
                self._extract_from_zip(chapter, file_path)
            elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
                with open(file_path, 'rb') as f:
                    page_count = chapter.pages.count()
                    self._save_page_image(chapter, f.read(), page_count + 1, os.path.basename(file_path))

            logger.info(f"Successfully processed {chapter}. Total pages: {chapter.pages.count()}")
            return True

        except Exception as e:
            logger.error(f"Error processing {chapter} from path: {e}")
            return False

    def _process_and_save_pages(self, chapter, tasks, file_path=None, archive_type=None):
        """Process page creations sequentially with per-image error handling."""
        from django.db.models import F
        from django.db import close_old_connections
        from administration.models import ChunkedUpload

        # Initialize total count
        if self.upload_id:
            ChunkedUpload.objects.filter(upload_id=self.upload_id).update(total_files_to_process=len(tasks), processed_files=0)

        saved_count = 0
        failed_count = 0

        for args in tasks:
            try:
                # Close stale DB connections before each iteration (important on long-running tasks)
                close_old_connections()

                # Extract image data
                if archive_type == 'zip':
                    i, inner_filename, filename = args
                    with zipfile.ZipFile(file_path, 'r') as zf:
                        with zf.open(inner_filename) as f:
                            image_data = f.read()
                elif archive_type == 'rar':
                    i, inner_filename, filename = args
                    with rarfile.RarFile(file_path, 'r') as rf:
                        with rf.open(inner_filename) as f:
                            image_data = f.read()
                elif archive_type == 'pdf':
                    i, page_num, img_idx, filename = args
                    reader = pypdf.PdfReader(file_path)
                    image_data = reader.pages[page_num].images[img_idx].data
                else:
                    i, image_data, filename = args

                # Save page (uploads to R2 + saves to DB atomically)
                self._save_page_image(chapter, image_data, i + 1, filename)
                saved_count += 1

                # Free memory immediately
                del image_data

                # Update progress tracking
                if self.upload_id:
                    ChunkedUpload.objects.filter(upload_id=self.upload_id).update(processed_files=F('processed_files') + 1)

            except Exception as e:
                failed_count += 1
                page_idx = args[0] if args else '?'
                logger.error(f"Failed to process page {page_idx} of {chapter}: {e}")
                # Continue to next image — don't let one failure kill the whole chapter
                continue

        logger.info(f"Finished processing {chapter}: {saved_count} saved, {failed_count} failed out of {len(tasks)}")

    def _save_page_image(self, chapter, image_data, page_number, filename):
        """Compress, resize, and save a page image to R2."""
        try:
            img = Image.open(BytesIO(image_data))
            # Free the raw data immediately
            del image_data

            # Convert to RGB if necessary (strips alpha channel, handles palette PNGs)
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')

            # Resize: cap width at 1400px (standard manga reader width)
            MAX_WIDTH = 1400
            if img.width > MAX_WIDTH:
                ratio = MAX_WIDTH / img.width
                new_height = int(img.height * ratio)
                img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)

            # Compress to JPEG at 82% quality (~200-400KB per page)
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=82, optimize=True)
            img.close()

            compressed_data = buffer.getvalue()
            buffer.close()

            # Force .jpg extension
            base = os.path.splitext(filename)[0]
            filename = f"{base}.jpg"

            page = Page(chapter=chapter, page_number=page_number)
            page.image.save(filename, ContentFile(compressed_data), save=True)

            del compressed_data
            return page

        except Exception as e:
            # Fallback: save raw data if compression fails
            logger.warning(f"Image compression failed for page {page_number}, saving raw: {e}")
            page = Page(chapter=chapter, page_number=page_number)
            page.image.save(filename, ContentFile(image_data if 'image_data' in dir() else b''), save=True)
            return page

    def _extract_from_pdf(self, chapter, file_path):
        """Extract images from PDF files."""
        chapter.pages.all().delete()
        
        reader = pypdf.PdfReader(file_path)
        
        tasks = []
        count = 0 
        for page_num, page in enumerate(reader.pages):
            for img_idx, image_file_object in enumerate(page.images):
                # Don't preload data. Pass coordinates to thread.
                tasks.append((count, page_num, img_idx, image_file_object.name))
                count += 1
                
        self._process_and_save_pages(chapter, tasks, file_path=file_path, archive_type='pdf')

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
                
                tasks = []
                for i, filename in enumerate(image_files):
                    clean_name = os.path.basename(filename)
                    # Don't preload data into memory
                    tasks.append((i, filename, clean_name))
                        
                self._process_and_save_pages(chapter, tasks, file_path=file_path, archive_type='rar')
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
            
            tasks = []
            for i, filename in enumerate(image_files):
                clean_name = os.path.basename(filename)
                # Don't preload data into memory
                tasks.append((i, filename, clean_name))
                    
            self._process_and_save_pages(chapter, tasks, file_path=file_path, archive_type='zip')
