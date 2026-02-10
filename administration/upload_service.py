import os
import shutil
from django.conf import settings
from .models import ChunkedUpload

class ChunkedUploadService:
    @staticmethod
    def get_upload_dir(upload_id):
        """Returns the directory where chunks for a specific upload are stored."""
        path = os.path.join(settings.MEDIA_ROOT, 'temp_uploads', str(upload_id))
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
        
        # Update progress in DB
        upload = ChunkedUpload.objects.get(upload_id=upload_id)
        upload.received_chunks += 1
        if upload.received_chunks == upload.total_chunks:
            upload.status = 'processing'
        upload.save()
        
        return upload

    @staticmethod
    def assemble_file(upload_id):
        """Assembles all chunks into a final file."""
        upload = ChunkedUpload.objects.get(upload_id=upload_id)
        upload_dir = ChunkedUploadService.get_upload_dir(upload_id)
        final_file_path = os.path.join(settings.MEDIA_ROOT, 'temp_uploads', upload.filename)
        
        # Ensure the filename is safe
        safe_filename = os.path.basename(upload.filename)
        final_file_path = os.path.join(settings.MEDIA_ROOT, 'temp_uploads', safe_filename)

        with open(final_file_path, 'wb') as final_file:
            for i in range(upload.total_chunks):
                chunk_path = os.path.join(upload_dir, f"part_{i}")
                if not os.path.exists(chunk_path):
                    upload.status = 'failed'
                    upload.save()
                    raise FileNotFoundError(f"Chunk {i} missing for upload {upload_id}")
                
                with open(chunk_path, 'rb') as chunk:
                    final_file.write(chunk.read())
        
        upload.status = 'completed'
        upload.save()
        
        # Cleanup chunks (but keep the assembled file for the processor)
        # The processor will handle moving the assembled file to its final destination
        shutil.rmtree(upload_dir)
        
        return final_file_path

    @staticmethod
    def cleanup_expired_uploads():
        """Removes old temp files (to be called by a task)."""
        # Logic to delete folders older than 24h
        pass
