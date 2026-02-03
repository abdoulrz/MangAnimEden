from django.shortcuts import render
from django.conf import settings
from catalog.models import Page


def demo_view(request):
    """
    Vue de démonstration du lecteur de manga.
    Affiche la première page disponible dans la base de données.
    """
    try:
        # Récupère la première page disponible
        page = Page.objects.select_related('chapter__series').first()
    except Page.DoesNotExist:
        page = None
    
    return render(request, 'reader/demo.html', {
        'page': page,
        'STATIC_VERSION': settings.STATIC_VERSION
    })
