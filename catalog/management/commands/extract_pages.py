
from django.core.management.base import BaseCommand
from catalog.models import Chapter
from catalog.services import FileProcessor

class Command(BaseCommand):
    help = 'Extracts pages/images from chapter source files (PDF, CBZ, EPUB)'

    def add_arguments(self, parser):
        parser.add_argument('--pk', type=int, help='Process a specific chapter by ID')
        parser.add_argument('--all', action='store_true', help='Process all chapters with source files')
        parser.add_argument('--force', action='store_true', help='Reprocess chapters even if they have pages')

    def handle(self, *args, **options):
        processor = FileProcessor()
        
        chapters_query = Chapter.objects.exclude(source_file='')
        
        if options['pk']:
            chapters_query = chapters_query.filter(pk=options['pk'])
        elif not options['all']:
            self.stdout.write(self.style.WARNING("Please specify --pk or --all"))
            return

        total = chapters_query.count()
        self.stdout.write(f"Found {total} chapters to check...")
        
        processed_count = 0
        
        for chapter in chapters_query:
            # Skip if already has pages, unless force
            if chapter.pages.exists() and not options['force']:
                self.stdout.write(f"Skipping Chapter #{chapter.number} (Pages exist)")
                continue

            self.stdout.write(f"Processing Chapter #{chapter.number} (ID: {chapter.id})...")
            success = processor.process_chapter(chapter)
            
            if success:
                processed_count += 1
                self.stdout.write(self.style.SUCCESS(f"  SUCCESS: Extracted {chapter.pages.count()} pages."))
            else:
                self.stdout.write(self.style.ERROR(f"  FAILED: Could not process chapter."))

        self.stdout.write(self.style.SUCCESS(f"Done. Processed {processed_count} chapters."))
