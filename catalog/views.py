from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Series, Favorite, Review
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from django.core.paginator import Paginator

def catalog_index(request):
    """
    Page principale du catalogue de mangas avec recherche et filtrage.
    """
    query = request.GET.get('q', '')
    genre = request.GET.get('genre', '')
    type_filter = request.GET.get('type', '')
    order = request.GET.get('order', 'title') # Default sort by title

    # Base queryset with annotations to avoid N+1 queries
    from django.db.models import Count
    series_list = Series.objects.prefetch_related('genres').annotate(
        real_chapters_count=Count('chapters') # Using a different name to avoid conflict with denormalized field if needed, but let's just use it to override or supplement
    ).all()

    # Phase 5: Gating NSFW Content (Admins bypass)
    is_admin = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    is_age_verified = request.user.is_authenticated and getattr(request.user, 'age_verified', False)
    if not (is_admin or is_age_verified):
        series_list = series_list.filter(nsfw=False)

    # Filtering
    if query:
        from django.db.models import Q
        series_list = series_list.filter(
            Q(title__icontains=query) |
            Q(type__icontains=query) |
            Q(genres__name__icontains=query)
        ).distinct()
    
    if genre:
        series_list = series_list.filter(genres__name__icontains=genre)
    
    if type_filter:
        series_list = series_list.filter(type__iexact=type_filter)

    # Sorting
    if order == 'views':
        series_list = series_list.order_by('-views_count')
    elif order == 'rating':
        series_list = series_list.order_by('-average_rating')
    elif order == 'newest':
        series_list = series_list.order_by('-created_at')
    else:
        series_list = series_list.order_by('title')

    # Pagination
    paginator = Paginator(series_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    trending_series = Series.objects.only('id', 'title', 'cover', 'views_count').all().order_by('-views_count')[:5]
    
    return render(request, 'catalog/index.html', {
        'page_obj': page_obj,
        'trending_series': trending_series,
        'STATIC_VERSION': settings.STATIC_VERSION,
        'search_query': query,
        'current_genre': genre,
        'current_type': type_filter,
        'current_order': order,
    })

def manga_detail(request, series_id):
    """
    Page de détail d'un manga.
    Fetches the series and its chapters.
    """
    series = get_object_or_404(Series, pk=series_id)
    # Increment views atomatically
    from django.db.models import F
    series.views_count = F('views_count') + 1
    series.save(update_fields=['views_count'])
    chapters = series.chapters.all().order_by('number')
    
    last_read_chapter = None
    is_favorite = False
    
    # Who's Reading This? (Phase 2.5.2.1)
    # Get users who have read chapters from this series, ordered by most recent activity
    from django.contrib.auth import get_user_model
    User = get_user_model()
    from django.db.models import Max
    
    readers = User.objects.filter(
        reading_progress__chapter__series=series
    ).annotate(
        last_active=Max('reading_progress__last_read')
    ).order_by('-last_active').distinct()[:10]

    user_review = None
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, series=series).exists()
        user_review = series.reviews.filter(user=request.user).first()
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
        'readers': readers,
        'user_review': user_review,
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

@login_required
@require_POST
def submit_review(request, series_id):
    series = get_object_or_404(Series, pk=series_id)
    try:
        data = json.loads(request.body)
        rating = int(data.get('rating', 0))
        content = data.get('content', '').strip()
        
        if not (1 <= rating <= 5):
            return JsonResponse({'success': False, 'error': 'La note doit être entre 1 et 5.'})
            
        review, created = Review.objects.update_or_create(
            series=series,
            user=request.user,
            defaults={'rating': rating, 'content': content}
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Avis enregistré avec succès!',
            'average_rating': series.average_rating,
            'review_count': series.review_count,
            'review': {
                'nickname': request.user.nickname,
                'avatar': request.user.avatar.url if request.user.avatar else '',
                'rating': rating,
                'content': content,
                'date': review.updated_at.strftime('%d %b %Y')
            }
        })
    except ValueError:
         return JsonResponse({'success': False, 'error': 'Données invalides.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def search_api(request):
    """
    JSON endpoint for live search.
    Matches on: title, series type, or genre name.
    """
    from django.db.models import Q

    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse({'results': []})

    results = Series.objects.filter(
        Q(title__icontains=query) |
        Q(type__icontains=query) |
        Q(genres__name__icontains=query)
    ).distinct()

    # Phase 5: Gating NSFW Content (Admins bypass)
    is_admin = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    is_age_verified = request.user.is_authenticated and getattr(request.user, 'age_verified', False)
    if not (is_admin or is_age_verified):
        results = results.filter(nsfw=False)
        
    results = results[:8]

    data = []
    for s in results:
        data.append({
            'id': s.id,
            'title': s.title,
            'cover': s.cover.url if s.cover else settings.STATIC_URL + 'img/default_cover.jpg',
            'url': f'/catalogue/series/{s.id}/',
            'type': s.get_type_display() if hasattr(s, 'get_type_display') else s.type
        })

    return JsonResponse({'results': data})
