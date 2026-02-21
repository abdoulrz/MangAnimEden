import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = 'Initialize production data (Site, superuser from env vars, etc.)'

    def handle(self, *args, **options):
        # Initialize default site
        site, created = Site.objects.get_or_create(id=settings.SITE_ID)
        site.domain = 'manganimeden-374d1.web.app'
        site.name = 'MangAnimEDen'
        site.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully initialized Site: {site.domain}'))

        # Create superuser from environment variables (set in Render dashboard)
        from users.models import User

        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(self.style.WARNING(
                'Skipping superuser creation: DJANGO_SUPERUSER_USERNAME, '
                'DJANGO_SUPERUSER_EMAIL, or DJANGO_SUPERUSER_PASSWORD not set.'
            ))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS(f'Superuser already exists: {email}'))
            return

        User.objects.create_superuser(
            nickname=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f'Superuser created: {email}'))
