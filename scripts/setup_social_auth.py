import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def setup_social_app():
    # 1. Setup Site
    site, created = Site.objects.get_or_create(id=1)
    site.name = "localhost"
    site.domain = "localhost:8000"
    site.save()
    print(f"Site setup: {site.domain}")

    # 2. Setup SocialApp
    provider = 'google'
    app, created = SocialApp.objects.get_or_create(
        provider=provider,
        name='Google Auth'
    )
    if created:
        app.client_id = 'dummy-client-id-for-dev'
        app.secret = 'dummy-secret-for-dev'
        app.save()
        print(f"Created SocialApp for {provider}")
    else:
        print(f"SocialApp for {provider} already exists")

    # 3. Link Site to App
    if not app.sites.filter(id=site.id).exists():
        app.sites.add(site)
        print(f"Linked Site {site.domain} to SocialApp {provider}")
    else:
        print(f"Site {site.domain} already linked to SocialApp {provider}")

if __name__ == '__main__':
    setup_social_app()
