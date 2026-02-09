from django.core.management.base import BaseCommand
from administration.models import SystemLog

class Command(BaseCommand):
    help = 'Localizes historical admin system logs to French'

    def handle(self, *args, **options):
        logs = SystemLog.objects.all()
        replacements = [
            ("Created series:", "Série créée :"),
            ("Updated series:", "Série modifiée :"),
            ("Created genre:", "Genre créé :"),
            ("Updated genre:", "Genre modifié :"),
            ("Created chapter", "Chapitre créé"),
            (" for ", " pour "),
            ("Updated group:", "Groupe modifié :"),
            # Add more as needed
        ]
        
        count = 0
        for log in logs:
            updated = False
            for old, new in replacements:
                if old in log.details:
                    log.details = log.details.replace(old, new)
                    updated = True
            
            if updated:
                log.save()
                count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Successfully localized {count} log entries.'))
