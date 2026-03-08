import os
import shutil
import tempfile
from django.conf import settings
from .models import ChunkedUpload

class ChunkedUploadService:
    @staticmethod
    def get_upload_dir(upload_id):
        """Returns the directory where chunks for a specific upload are stored."""
        base_dir = getattr(settings, 'MEDIA_ROOT', tempfile.gettempdir())
        # Store chunks in a subfolder to avoid deleting the final file during cleanup
        path = os.path.join(base_dir, 'manga_temp_uploads', str(upload_id), 'chunks')
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def save_chunk(upload_id, chunk_file, index):
        """Saves a single chunk to the temporary directory."""
        upload_dir = ChunkedUploadService.get_upload_dir(upload_id)
        chunk_path = os.path.join(upload_dir, f"part_{index}")
        
        with open(chunk_path, 'wb+') as destination:
            for chunk in chunk_file.chunks():
                destination.write(chunk)
        
        # Update progress in DB atomically to avoid race conditions
        from django.db.models import F
        upload_qs = ChunkedUpload.objects.filter(upload_id=upload_id)
        upload_qs.update(received_chunks=F('received_chunks') + 1)
        
        # Refresh to check status
        upload_obj = ChunkedUpload.objects.get(upload_id=upload_id)
        if upload_obj.received_chunks >= upload_obj.total_chunks:
            upload_obj.status = 'processing'
            upload_obj.save(update_fields=['status'])
        
        return upload_obj

    @staticmethod
    def assemble_file(upload_id):
        """Assembles all chunks into a final file."""
        upload = ChunkedUpload.objects.get(upload_id=upload_id)
        chunk_dir = ChunkedUploadService.get_upload_dir(upload_id)
        
        base_dir = getattr(settings, 'MEDIA_ROOT', tempfile.gettempdir())
        # Final file sits in the upload_id root, NOT in chunks/
        final_dir = os.path.join(base_dir, 'manga_temp_uploads', str(upload_id))
        os.makedirs(final_dir, exist_ok=True)
        
        safe_filename = os.path.basename(upload.filename)
        final_file_path = os.path.join(final_dir, safe_filename)

        with open(final_file_path, 'wb') as final_file:
            for i in range(upload.total_chunks):
                chunk_path = os.path.join(chunk_dir, f"part_{i}")
                if not os.path.exists(chunk_path):
                    upload.status = 'failed'
                    upload.save(update_fields=['status'])
                    raise FileNotFoundError(f"Chunk {i} missing for upload {upload_id}")
                
                with open(chunk_path, 'rb') as chunk:
                    # Write in blocks to save memory
                    while True:
                        data = chunk.read(1024 * 1024) # 1MB blocks
                        if not data:
                            break
                        final_file.write(data)
        
        upload.status = 'completed'
        upload.save(update_fields=['status'])
        
        # Cleanup ONLY the chunks folder, leaving the assembled file safe in final_dir
        if os.path.exists(chunk_dir):
            shutil.rmtree(chunk_dir)
        
        return final_file_path

    @staticmethod
    def cleanup_expired_uploads():
        """Removes old temp files (to be called by a task)."""
        # Logic to delete folders older than 24h
        pass
