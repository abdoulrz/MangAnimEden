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

    # --- Friend Stats (Phase 2.5.2) ---
    context['friend_count'] = request.user.get_friend_count()
    context['pending_requests'] = request.user.get_pending_requests()
    context['pending_count'] = request.user.get_pending_requests_count()

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

    # Self-healing: Ensure level in DB matches XP formula (Fix for Lvl 51 issue)
    calculated_level = request.user.calculate_level()
    if request.user.level != calculated_level:
        request.user.level = calculated_level
        request.user.save(update_fields=['level'])

    # Level Progress
    context['level_data'] = request.user.get_level_progress()

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

    # --- Badges (Phase 2.5.3) ---
    from .models import Badge, UserBadge
    
    # All badges sorted by threshold to form the timeline
    # Note: This simple sort assumes all badges are comparable (e.g. all CHAPTERS_READ).
    # For mixed types, we might want to group them or sort by complex logic.
    # For now, we assume primary path is Reading.
    
    all_badges = Badge.objects.all().order_by('threshold')
    user_badges_qs = UserBadge.objects.filter(user=request.user).select_related('badge')
    user_badges_map = {ub.badge.id: ub for ub in user_badges_qs}
    
    timeline_badges = []
    first_locked_found = False
    
    for badge in all_badges:
        if badge.id in user_badges_map:
            status = 'unlocked'
            obtained_at = user_badges_map[badge.id].obtained_at
        else:
            if not first_locked_found:
                status = 'next'
                first_locked_found = True
            else:
                status = 'locked'
            obtained_at = None
            
        timeline_badges.append({
            'badge': badge,
            'status': status,
            'obtained_at': obtained_at
        })
        
    context['timeline_badges'] = timeline_badges
    context['user_badges_count'] = len(user_badges_map)
    context['total_badges_count'] = len(timeline_badges)

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
    DEPRECATED: Redirect to profile.
    Old Description: Page Domaine - Dashboard utilisateur avec Quick Access, Stats, et History.
    """
    # Preserve query params for smooth transition if needed (e.g. ?mode=scans)
    query_string = request.META.get('QUERY_STRING', '')
    url = redirect('users:profile').url
    if query_string:
        url = f"{url}?{query_string}"
    return redirect(url)

@login_required
def public_profile_view(request, user_id):
    """
    Vue du profil public d'un utilisateur (Phase 2.5.2 - Friend Discovery).
    Permet de voir le profil d'un autre utilisateur et d'envoyer une demande d'ami.
    """
    from reader.models import ReadingProgress
    from catalog.models import Series
    
    # Get the profile user
    profile_user = get_object_or_404(User, id=user_id)
    
    # Redirect to own profile if viewing self
    if profile_user == request.user:
        return redirect('users:profile')
    
    # Determine friendship status
    is_friend = request.user.is_friend_with(profile_user)
    has_pending_from = request.user.has_pending_request_from(profile_user)
    has_sent_to = request.user.has_sent_request_to(profile_user)
    
    # Self-healing for public profile view as well
    calculated_level = profile_user.calculate_level()
    if profile_user.level != calculated_level:
        profile_user.level = calculated_level
        profile_user.save(update_fields=['level'])
    
    # Get public stats
    total_chapters = ReadingProgress.objects.filter(user=profile_user).count()
    series_in_progress_count = ReadingProgress.objects.filter(
        user=profile_user
    ).values('chapter__series').distinct().count()
    
    context = {
        'profile_user': profile_user,
        'is_friend': is_friend,
        'has_pending_from': has_pending_from,
        'has_sent_to': has_sent_to,
        'friend_count': profile_user.get_friend_count(),
        'level_data': profile_user.get_level_progress(),
        'stats': {
            'total_chapters': total_chapters,
            'series_in_progress': series_in_progress_count,
        },
        'STATIC_VERSION': settings.STATIC_VERSION
    }
    
    return render(request, 'users/public_profile.html', context)

