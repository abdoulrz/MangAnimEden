from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Series, Favorite
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

def catalog_index(request):
    """
    Page principale du catalogue de mangas.
    """
    series_list = Series.objects.all().order_by('-updated_at')
    trending_series = Series.objects.all().order_by('-views_count')[:5]
    return render(request, 'catalog/index.html', {
        'series_list': series_list,
        'trending_series': trending_series,
        'STATIC_VERSION': settings.STATIC_VERSION
    })

def manga_detail(request, series_id):
    """
    Page de détail d'un manga.
    Fetches the series and its chapters.
    """
    series = get_object_or_404(Series, pk=series_id)
    # Increment views
    series.views_count += 1
    series.save(update_fields=['views_count'])
    chapters = series.chapters.all().order_by('number')
    
    last_read_chapter = None
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, series=series).exists()
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
        'is_favorite': is_favorite,
        'STATIC_VERSION': settings.STATIC_VERSION
    })

@login_required
@require_POST
def toggle_favorite(request, series_id):
    series = get_object_or_404(Series, pk=series_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, series=series)
    
    if not created:
        favorite.delete()
        is_favorite = False
    else:
        is_favorite = True
        
    return JsonResponse({'is_favorite': is_favorite})
