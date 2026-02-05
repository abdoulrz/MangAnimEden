from django.core.management.base import BaseCommand
from django.utils import timezone
from social.models import Story

class Command(BaseCommand):
    help = 'Supprime les stories expirées (anciennes de plus de 24h)'

    def handle(self, *args, **options):
        now = timezone.now()
        expired_stories = Story.objects.filter(expires_at__lt=now)
        count = expired_stories.count()
        
        if count > 0:
            # La suppression déclenchera le signal post_delete pour supprimer les fichiers
            expired_stories.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} expired stories'))
        else:
            self.stdout.write(self.style.SUCCESS('No expired stories found'))
