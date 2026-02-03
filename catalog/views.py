from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Series

def catalog_index(request):
    """
    Page principale du catalogue de mangas.
    """
    series_list = Series.objects.all().order_by('-updated_at')
    return render(request, 'catalog/index.html', {
        'series_list': series_list,
        'STATIC_VERSION': settings.STATIC_VERSION
    })

def manga_detail(request, series_id):
    """
    Page de détail d'un manga.
    Fetches the series and its chapters.
    """
    series = get_object_or_404(Series, pk=series_id)
    chapters = series.chapters.all().order_by('number')
    
    last_read_chapter = None
    if request.user.is_authenticated:
        # Avoid circular import if possible, or import inside
        from reader.models import ReadingProgress
        last_read = ReadingProgress.objects.filter(
            user=request.user, 
            chapter__series=series
        ).order_by('-last_read').first()
        if last_read:
            last_read_chapter = last_read.chapter

    return render(request, 'catalog/detail.html', {
        'series': series,
        'chapters': chapters,
        'last_read_chapter': last_read_chapter,
        'STATIC_VERSION': settings.STATIC_VERSION
    })
