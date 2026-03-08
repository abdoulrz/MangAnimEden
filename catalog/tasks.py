import os
import logging
from celery import shared_task
from catalog.services import process_single_chapter_from_temp

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def task_process_chapter(self, series_id, upload_id, temp_file_path):
    """
    Celery task to process a single chapter from a temp file.
    
    Args:
        series_id: ID of the Series to attach the chapter to.
        upload_id: UUID string of ChunkedUpload record (can be None for single-file uploads).
        temp_file_path: Path to the temp file on disk.
    """
    from administration.models import ChunkedUpload
    from catalog.services import FileProcessor

    upload = None
    if upload_id:
        try:
            upload = ChunkedUpload.objects.get(upload_id=upload_id)
        except ChunkedUpload.DoesNotExist:
            logger.warning(f"ChunkedUpload {upload_id} not found, proceeding without tracking.")

    def _mark_failed(reason=""):
        """Mark upload as failed and clean up temp file."""
        if upload:
            upload.status = 'failed'
            upload.save(update_fields=['status'])
        _cleanup_file()
        if reason:
            logger.error(f"Upload {upload_id} failed: {reason}")

    def _cleanup_file():
        """Safely remove the temp file and its parent folder if empty."""
        try:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
            # Attempt to delete the parent upload_id directory if empty
            if upload_id:
                parent_dir = os.path.dirname(temp_file_path)
                if os.path.basename(parent_dir) == str(upload_id):
                    os.rmdir(parent_dir)
        except OSError:
            pass

    # Mark as processing immediately so the polling view knows we're active
    if upload and upload.status != 'processing':
        upload.status = 'processing'
        upload.save(update_fields=['status'])

    # --- Check file exists ---
    if not os.path.exists(temp_file_path):
        # Try safe filename fallback
        from django.conf import settings
        import tempfile as tmpmod
        base_dir = getattr(settings, 'MEDIA_ROOT', tmpmod.gettempdir())
        base_temp_dir = os.path.join(base_dir, 'manga_temp_uploads')
        if upload:
            safe_filename = os.path.basename(upload.filename)
            alt_path = os.path.join(base_temp_dir, str(upload_id), safe_filename)
            if not os.path.exists(alt_path):
                # Fallback purely in case it was stored without the upload_id directory
                alt_path = os.path.join(base_temp_dir, safe_filename)
            if os.path.exists(alt_path):
                temp_file_path = alt_path

    if not os.path.exists(temp_file_path):
        _mark_failed(f"File not found: {temp_file_path}")
        return  # Don't retry — file won't magically appear

    # --- Process the chapter ---
    try:
        if upload:
            chapter = process_single_chapter_from_temp(
                series_id, temp_file_path, upload_id=upload_id
            )
            logger.info(f"Celery processed chapter {chapter.number} for series {series_id}")
            _cleanup_file()
            upload.status = 'completed'
            upload.save(update_fields=['status'])
        else:
            # Single-file upload: chapter already exists, just extract pages
            from catalog.models import Series
            processor = FileProcessor()
            series = Series.objects.get(id=series_id)
            latest_chapter = series.chapters.order_by('-id').first()
            if latest_chapter:
                processor._process_from_path(latest_chapter, temp_file_path)
                logger.info(f"Celery processed chapter {latest_chapter.number} from single upload")
            _cleanup_file()

    except ValueError as exc:
        # Non-retryable: bad filename, missing chapter number, etc.
        _mark_failed(f"Non-retryable error: {exc}")
        return  # Don't retry — same error will happen again

    except Exception as exc:
        logger.error(f"Celery task error for upload {upload_id}: {exc}")
        if upload:
            upload.status = 'failed'
            upload.save(update_fields=['status'])
        # Only clean up the file on FINAL retry (no more retries left)
        if self.request.retries >= self.max_retries:
            _cleanup_file()
            return  # Give up
        # Don't delete the file — retry needs it
        raise self.retry(exc=exc)

@shared_task
def task_bulk_process_chapters(series_id, upload_ids):
    """
    Celery task that loops through multiple upload_ids and dispatches individual processing tasks.
    Offloading the loop from the web server thread to the worker prevents DB locking issues.
    """
    import os
    from administration.models import ChunkedUpload
    from django.conf import settings
    import tempfile as tmpmod

    base_dir = getattr(settings, 'MEDIA_ROOT', tmpmod.gettempdir())
    base_temp_dir = os.path.join(base_dir, 'manga_temp_uploads')

    for upload_id in upload_ids:
        try:
            upload = ChunkedUpload.objects.get(upload_id=upload_id)
            
            # Construct the path to the assembled file
            safe_filename = os.path.basename(upload.filename)
            temp_path = os.path.join(base_temp_dir, str(upload_id), safe_filename)

            if not os.path.exists(temp_path):
                # Fallback for older flat structure
                temp_path = os.path.join(base_temp_dir, safe_filename)

            if os.path.exists(temp_path):
                # Dispatch individual chapter task
                task_process_chapter.delay(series_id, str(upload_id), temp_path)
            else:
                logger.error(f"Bulk process: temp file not found for upload {upload_id}")
                upload.status = 'failed'
                upload.save(update_fields=['status'])
                
        except Exception as e:
            logger.error(f"Error dispatching bulk item {upload_id}: {e}")
            continue

