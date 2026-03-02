import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=10)
def task_process_story_media(self, story_id):
    """
    Celery task to optimize story media (resize, compress).
    Placeholder for future enhancement when story images need optimization.
    """
    from social.models import Story
    from PIL import Image
    from io import BytesIO
    from django.core.files.base import ContentFile
    import os

    try:
        story = Story.objects.get(id=story_id)

        if not story.image:
            logger.info(f"Story {story_id} has no image, skipping media processing.")
            return

        # Open and optimize the image
        img = Image.open(story.image)

        # Convert to RGB if needed
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')

        # Cap width at 1080px for stories
        MAX_WIDTH = 1080
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            new_height = int(img.height * ratio)
            img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)

        # Compress to JPEG
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        img.close()

        compressed = buffer.getvalue()
        buffer.close()

        # Overwrite with optimized version
        base = os.path.splitext(os.path.basename(story.image.name))[0]
        story.image.save(f"{base}_opt.jpg", ContentFile(compressed), save=True)

        del compressed
        logger.info(f"Story {story_id} media optimized successfully.")

    except Story.DoesNotExist:
        logger.error(f"Story {story_id} does not exist.")
    except Exception as exc:
        logger.error(f"Error processing story {story_id} media: {exc}")
        raise self.retry(exc=exc)
