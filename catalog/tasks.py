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
        """Safely remove the temp file."""
        try:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        except OSError:
            pass

    # Mark as processing immediately so the polling view knows we're active
    if upload and upload.status != 'processing':
        upload.status = 'processing'
        upload.save(update_fields=['status'])

    # --- Check file exists ---
    if not os.path.exists(temp_file_path):
        # Try safe filename fallback
        import tempfile as tmpmod
        base_temp_dir = os.path.join(tmpmod.gettempdir(), 'manga_temp_uploads')
        if upload:
            safe_filename = os.path.basename(upload.filename)
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
