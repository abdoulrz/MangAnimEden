from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings

class Command(BaseCommand):
    help = 'Initialize production data (Site, etc.)'

    def handle(self, *args, **options):
        # Initialize default site
        site, created = Site.objects.get_or_create(id=settings.SITE_ID)
        site.domain = 'manganimeden-374d1.web.app'
        site.name = 'MangAnimEDen'
        site.save()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully initialized Site: {site.domain}'))

        # Create a test user for production testing (since SQLite is ephemeral)
        from users.models import User
        test_email = 'test@manganimeden.com'
        if not User.objects.filter(email=test_email).exists():
            User.objects.create_superuser(
                nickname='TestAdmin',
                email=test_email,
                password='Password123!'
            )
            self.stdout.write(self.style.SUCCESS(f'Created test admin: {test_email} / Password123!'))
        else:
            self.stdout.write(self.style.SUCCESS('Test user already exists.'))
