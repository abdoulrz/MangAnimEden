from django.shortcuts import render
from django.conf import settings


def catalog_index(request):
    """
    Page principale du catalogue de mangas.
    """
    return render(request, 'catalog/index.html', {
        'STATIC_VERSION': settings.STATIC_VERSION
    })

def manga_detail(request):
    """
    Page de détail d'un manga (Mock).
    """
    return render(request, 'catalog/detail.html', {
        'STATIC_VERSION': settings.STATIC_VERSION
    })
