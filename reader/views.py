from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse
from catalog.models import Chapter, Page
import logging

logger = logging.getLogger(__name__)


def _get_chapter(series_slug, chapter_number):
    """Resolve a chapter from its series slug and number."""
    return get_object_or_404(
        Chapter.objects.select_related('series'),
        series__slug=series_slug,
        number=chapter_number,
    )


def chap_legacy_redirect(request, chapter_id):
    """Permanent redirect from /reader/chap/<id>/ to the clean slug URL."""
    chapter = get_object_or_404(Chapter.objects.select_related('series'), id=chapter_id)
    return redirect(
        'reader:chap_chapter',
        series_slug=chapter.series.slug,
        chapter_number=str(chapter.number),
        permanent=True,
    )


def chap_view(request, series_slug=None, chapter_number=None):
    """
    Vue du lecteur de manga.
    Accepte un slug de série + numéro de chapitre, ou aucun paramètre.
    """
    if series_slug and chapter_number:
        chapter = _get_chapter(series_slug, chapter_number)
    else:
        # Récupère le premier chapitre disponible
        chapter = Chapter.objects.select_related('series').first()
        if chapter:
            return redirect('reader:chap_chapter',
                            series_slug=chapter.series.slug,
                            chapter_number=str(chapter.number))

    if not chapter:
        return render(request, 'reader/chap.html', {
            'page': None,
            'STATIC_VERSION': settings.STATIC_VERSION
        })
    
    # Phase 5: Gating NSFW Content (Biological Age Logic)
    if chapter.series.nsfw:
        is_admin = request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
        if not is_admin:
            if not request.user.is_authenticated or not request.user.birth_date:
                return render(request, 'reader/nsfw_warning.html', {'STATIC_VERSION': settings.STATIC_VERSION})
            if not request.user.is_major:
                return render(request, 'reader/nsfw_denied.html', {'STATIC_VERSION': settings.STATIC_VERSION})
    
    # Phase 5: Gating Logic & Monetization
    # We define premium as: chapter flag is true, OR chapter number > 50
    is_chapter_premium = chapter.is_premium or float(chapter.number) > 50
    # Overrides for users with active Otaku Premium membership or admins
    if request.user.is_authenticated:
        if getattr(request.user, 'is_premium', False) or request.user.is_staff or request.user.is_superuser:
            is_chapter_premium = False

    if is_chapter_premium:
        if not request.user.is_authenticated:
            return render(request, 'reader/paywall.html', {'chapter': chapter, 'STATIC_VERSION': settings.STATIC_VERSION})
        
        from reader.models import UnlockedChapter
        from users.models import UserWallet
        from django.db import transaction as db_transaction
        
        has_unlocked = UnlockedChapter.objects.filter(user=request.user, chapter=chapter).exists()
        
        if not has_unlocked:
            wallet = getattr(request.user, 'wallet', None)
            chapter_price = 20 # Static cost for a chapter
                
            if wallet and wallet.auto_use_credits and wallet.credits_balance >= chapter_price:
                # Auto-deduct safely
                with db_transaction.atomic():
                    wallet_locked = UserWallet.objects.select_for_update().get(id=wallet.id)
                    if wallet_locked.credits_balance >= chapter_price:
                        wallet_locked.credits_balance -= chapter_price
                        wallet_locked.save()
                        UnlockedChapter.objects.create(user=request.user, chapter=chapter)
                        logger.info(f"Auto-débit: user={request.user.nickname}, chapter={chapter.id}, price={chapter_price} Orbes")
                    else:
                        return render(request, 'reader/paywall.html', {'chapter': chapter, 'STATIC_VERSION': settings.STATIC_VERSION, 'wallet': wallet})
            else:
                # Ask user to buy or use credits manually
                return render(request, 'reader/paywall.html', {'chapter': chapter, 'STATIC_VERSION': settings.STATIC_VERSION, 'wallet': wallet})

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
    
    # Recommendations (Phase 3.4.2)
    from catalog.models import Series
    from django.db.models import Count
    
    recommendations = Series.objects.filter(
        genres__in=chapter.series.genres.all()
    ).exclude(
        id=chapter.series.id
    ).annotate(
        shared_genres=Count('genres')
    ).order_by('-shared_genres', '-views_count')[:4]
    
    # Context
    context = {
        'page': first_page, # For backward compatibility with existing template logic that expects 'page'
        'chapter': chapter,
        'pages': pages,
        'current_page': current_page,
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter,
        'recommendations': recommendations,
        'STATIC_VERSION': settings.STATIC_VERSION
    }
    
    return render(request, 'reader/chap.html', context)

# ─── Phase 5: Manual Chapter Unlock ───────────────────────────────────────────

CHAPTER_PRICE = 20  # crédits par chapitre premium


@login_required
@require_POST
def unlock_chapter(request, series_slug, chapter_number):
    """
    Débloque manuellement un chapitre premium en déduisant CHAPTER_PRICE crédits.
    Idempotent : si déjà débloqué, renvoie success=True sans re-déduire.

    POST /reader/unlock/<series_slug>/<chapter_number>/
    Retourne: { success: bool, redirect?: str, error?: str, balance?: int }
    """
    from reader.models import UnlockedChapter
    from users.models import UserWallet
    from django.db import transaction as db_transaction

    chapter = _get_chapter(series_slug, chapter_number)
    redirect_url = reverse('reader:chap_chapter',
                           kwargs={'series_slug': series_slug, 'chapter_number': chapter_number})

    # Idempotent: already unlocked → no charge
    if UnlockedChapter.objects.filter(user=request.user, chapter=chapter).exists():
        return JsonResponse({
            'success': True,
            'already_unlocked': True,
            'redirect': redirect_url,
        })

    wallet = getattr(request.user, 'wallet', None)
    if not wallet:
        return JsonResponse({'success': False, 'error': 'Portefeuille introuvable.'}, status=400)

    with db_transaction.atomic():
        wallet_locked = UserWallet.objects.select_for_update().get(id=wallet.id)

        if wallet_locked.credits_balance < CHAPTER_PRICE:
            return JsonResponse({
                'success': False,
                'error': f'Crédits insuffisants. Il vous faut {CHAPTER_PRICE} crédits.',
                'balance': wallet_locked.credits_balance,
                'required': CHAPTER_PRICE,
            }, status=402)

        wallet_locked.credits_balance -= CHAPTER_PRICE
        wallet_locked.save(update_fields=['credits_balance'])
        UnlockedChapter.objects.create(user=request.user, chapter=chapter)
        logger.info(f"Déblocage manuel: user={request.user.nickname}, chapter={chapter.id}, price={CHAPTER_PRICE} Orbes")

    return JsonResponse({
        'success': True,
        'redirect': redirect_url,
        'new_balance': wallet_locked.credits_balance,
    })
