import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sites.models import Site

def update_site(domain):
    """
    Updates the default Site (ID=1) with the provided domain.
    """
    site, created = Site.objects.get_or_create(id=1)
    site.domain = domain
    site.name = domain
    site.save()
    print(f"Successfully updated Site (ID=1) to: {domain}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        new_domain = sys.argv[1]
    else:
        # Try to detect from environment or use local default
        new_domain = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '127.0.0.1:8000')
    
    update_site(new_domain)
