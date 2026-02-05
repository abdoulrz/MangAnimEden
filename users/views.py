from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import UserUpdateForm
from core.decorators import requires_admin
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from catalog.models import Series
from collections import defaultdict

User = get_user_model()

@requires_admin
def admin_dashboard(request):
    """
    Tableau de bord pour l'administration métier (Site Administrators).
    Permet de gérer les utilisateurs et d'ajouter du contenu.
    """
    users = User.objects.all().order_by('-date_joined')
    recent_series = Series.objects.all().order_by('-updated_at')[:5]

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        if user_id and action:
            target_user = get_object_or_404(User, id=user_id)
            if action == 'toggle_admin':
                 # Prevent removing own admin status to avoid lockout, logic can be improved
                if target_user != request.user:
                    target_user.role_admin = not target_user.role_admin
            elif action == 'toggle_moderator':
                target_user.role_moderator = not target_user.role_moderator
            elif action == 'toggle_ban':
                target_user.is_banned = not target_user.is_banned
            
            target_user.save()
            return redirect('users:admin_dashboard')

    return render(request, 'users/admin_dashboard.html', {
        'users': users,
        'recent_series': recent_series,
        'STATIC_VERSION': settings.STATIC_VERSION
    })

@login_required
def profile_view(request):
    """
    Vue du profil utilisateur.
    """
    from reader.models import ReadingProgress
    from catalog.models import Favorite, Series
    from django.utils import timezone
    from datetime import timedelta
    from collections import defaultdict

    context = {
        'STATIC_VERSION': settings.STATIC_VERSION
    }

    # --- Stats ---
    total_chapters = ReadingProgress.objects.filter(user=request.user).count()
    series_in_progress_count = ReadingProgress.objects.filter(
        user=request.user
    ).values('chapter__series').distinct().count()
    
    # Calculate finished series
    finished_series_count = 0
    # Get IDs of series user has read at least one chapter of
    user_series_ids = ReadingProgress.objects.filter(user=request.user).values_list('chapter__series', flat=True).distinct()
    
    for series_id in user_series_ids:
        series_obj = Series.objects.get(id=series_id)
        total_chapters_count = series_obj.chapters.count()
        if total_chapters_count > 0:
            user_completed_count = ReadingProgress.objects.filter(
                user=request.user, 
                chapter__series=series_obj, 
                completed=True
            ).count()
            if user_completed_count == total_chapters_count:
                finished_series_count += 1

    
    context['stats'] = {
        'total_chapters': total_chapters,
        'series_in_progress': series_in_progress_count,
        'finished_series': finished_series_count,
    }

    # --- Favoris ---
    favorites = Favorite.objects.filter(user=request.user).select_related('series')
    context['favoris'] = [f.series for f in favorites]

    # --- History ---
    recent_progress = ReadingProgress.objects.filter(
        user=request.user
    ).select_related('chapter__series').order_by('-last_read')[:50]
    
    series_progress = defaultdict(list)
    for progress in recent_progress:
        series_progress[progress.chapter.series].append(progress)
    
    # context['recent_progress'] = recent_progress # Optional if not used directly
    context['series_progress'] = dict(series_progress)

    # --- Scans (Started Series) ---
    user_series_ids = ReadingProgress.objects.filter(
        user=request.user
    ).values_list('chapter__series', flat=True).distinct()
    context['scans'] = Series.objects.filter(id__in=user_series_ids)

    # Default active mode for the view (can be ignored by JS if we toggle all)
    context['active_mode'] = 'overview' 

    return render(request, 'users/profile.html', context)

@login_required
def edit_profile_view(request):
    """
    Vue pour modifier le profil utilisateur.
    """
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {
        'form': form,
        'STATIC_VERSION': settings.STATIC_VERSION
    })

@login_required
def domaine_view(request):
    """
    Page Domaine - Dashboard utilisateur avec Quick Access, Stats, et History.
    """
    from reader.models import ReadingProgress
    from django.utils import timezone
    from datetime import timedelta
    
    # Get active mode from query params (quick_access, stats, history)
    active_mode = request.GET.get('mode', 'quick_access')
    active_submenu = request.GET.get('submenu', '')  # For quick access submenus
    
    context = {
        'active_mode': active_mode,
        'active_submenu': active_submenu,
        'STATIC_VERSION': settings.STATIC_VERSION
    }
    
    # Load data based on active mode
    if active_mode == 'stats':
        # Calculate reading statistics
        total_chapters = ReadingProgress.objects.filter(user=request.user).count()
        series_in_progress = ReadingProgress.objects.filter(
            user=request.user
        ).values('chapter__series').distinct().count()
        
        # Calculate finished series
        finished_series_count = 0
        # Get IDs of series user has read at least one chapter of
        user_series_ids = ReadingProgress.objects.filter(user=request.user).values_list('chapter__series', flat=True).distinct()
        
        for series_id in user_series_ids:
            series_obj = Series.objects.get(id=series_id)
            total_chapters_count = series_obj.chapters.count()
            if total_chapters_count > 0:
                user_completed_count = ReadingProgress.objects.filter(
                    user=request.user, 
                    chapter__series=series_obj, 
                    completed=True
                ).count()
                if user_completed_count == total_chapters_count:
                    finished_series_count += 1
        
        context['stats'] = {
            'total_chapters': total_chapters,
            'series_in_progress': series_in_progress,
            'finished_series': finished_series_count,
        }

    elif active_mode == 'favoris':
        # Load user favorites
        from catalog.models import Favorite
        favorites = Favorite.objects.filter(user=request.user).select_related('series')
        context['favoris'] = [f.series for f in favorites]
    
    elif active_mode == 'history':
        # Get recent reading history
        recent_progress = ReadingProgress.objects.filter(
            user=request.user
        ).select_related('chapter__series').order_by('-last_read')[:50]
        
        # Group by series
        series_progress = defaultdict(list)
        for progress in recent_progress:
            series_progress[progress.chapter.series].append(progress)
        
        context['recent_progress'] = recent_progress
        context['series_progress'] = dict(series_progress)
    
    elif active_mode == 'quick_access' and active_submenu:
        # Handle quick access submenus
        if active_submenu == 'scans':
            # Get all series user has started reading (could extend with favorites later)
            user_series_ids = ReadingProgress.objects.filter(
                user=request.user
            ).values_list('chapter__series', flat=True).distinct()
            context['scans'] = Series.objects.filter(id__in=user_series_ids)
        # Add other submenus as needed (favoris, equipes, etc.)
    
    return render(request, 'users/domaine.html', context)

