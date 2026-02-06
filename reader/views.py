from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from catalog.models import Chapter, Page


def demo_view(request, chapter_id=None):
    """
    Vue de démonstration du lecteur de manga.
    Peut afficher un chapitre spécifique ou le premier disponible.
    """
    if chapter_id:
        chapter = get_object_or_404(Chapter.objects.select_related('series'), id=chapter_id)
    else:
        # Récupère le premier chapitre disponible
        chapter = Chapter.objects.select_related('series').first()
        if chapter:
            return redirect('reader:demo_chapter', chapter_id=chapter.id)

    if not chapter:
        return render(request, 'reader/demo.html', {
            'page': None,
            'STATIC_VERSION': settings.STATIC_VERSION
        })
    
    # Get pages if image-based
    pages = chapter.pages.all().order_by('page_number')
    first_page = pages.first() if pages.exists() else None
    
    # Navigation
    prev_chapter = Chapter.objects.filter(series=chapter.series, number__lt=chapter.number).order_by('-number').first()
    next_chapter = Chapter.objects.filter(series=chapter.series, number__gt=chapter.number).order_by('number').first()
    
    # Save Reading Progress & Mark as Completed (awards XP via signal)
    if request.user.is_authenticated:
        from reader.models import ReadingProgress
        progress, created = ReadingProgress.objects.update_or_create(
            user=request.user,
            chapter=chapter,
            defaults={'completed': True}  # Mark as completed to award XP
        )
    
    # Context
    context = {
        'page': first_page, # For backward compatibility with existing template logic that expects 'page'
        'chapter': chapter,
        'pages': pages,
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter,
        'STATIC_VERSION': settings.STATIC_VERSION
    }
    
    return render(request, 'reader/demo.html', context)
