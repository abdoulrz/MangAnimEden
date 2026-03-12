from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from catalog.models import Chapter, Page


def chap_view(request, chapter_id=None):
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
            return redirect('reader:chap_chapter', chapter_id=chapter.id)

    if not chapter:
        return render(request, 'reader/chap.html', {
            'page': None,
            'STATIC_VERSION': settings.STATIC_VERSION
        })
    
    # Get pages if image-based
    pages = chapter.pages.all().order_by('page_number')
    first_page = pages.first() if pages.exists() else None
    
    # Navigation
    prev_chapter = Chapter.objects.filter(series=chapter.series, number__lt=chapter.number).order_by('-number').first()
    next_chapter = Chapter.objects.filter(series=chapter.series, number__gt=chapter.number).order_by('number').first()
    
    # Save Reading Progress (without marking completed)
    current_page = 1
    if request.user.is_authenticated:
        from reader.models import ReadingProgress
        progress, created = ReadingProgress.objects.get_or_create(
            user=request.user,
            chapter=chapter,
        )
        
        # If this chapter was marked completed by the old auto-complete system
        # but the user is opening it again, reset the stale completion.
        # The chapter will only be re-completed when the API confirms the user
        # has truly reached the last page. XP is protected by the pre_save signal.
        if progress.completed:
            total_pages = chapter.pages.count()
            # Only reset if current_page hasn't actually reached the end
            # (this is the telltale sign of stale old data)
            if progress.current_page < total_pages:
                progress.completed = False
        
        progress.save()  # Update last_read
        current_page = progress.current_page
    else:
        # Phase 3.6: Accès Limité (Stratégie de Conversion)
        # Track read chapters for anonymous users in session
        free_chapters = request.session.get('free_chapters_read', [])
        
        if chapter.id not in free_chapters:
            if len(free_chapters) >= 3:
                # Limit reached, redirect to conversion page
                return render(request, 'reader/limit_reached.html', {
                    'chapter': chapter,
                    'STATIC_VERSION': settings.STATIC_VERSION
                })
            else:
                free_chapters.append(chapter.id)
                request.session['free_chapters_read'] = free_chapters
                request.session.modified = True
    
    # Context
    context = {
        'page': first_page, # For backward compatibility with existing template logic that expects 'page'
        'chapter': chapter,
        'pages': pages,
        'current_page': current_page,
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter,
        'STATIC_VERSION': settings.STATIC_VERSION
    }
    
    return render(request, 'reader/chap.html', context)
