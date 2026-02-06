from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Group, Event, Message, Story
from django.contrib.auth import get_user_model
from django.db import models
User = get_user_model()
from django.utils import timezone
from core.decorators import requires_moderator

# ... (delete_message remains the same)

@requires_moderator
def delete_message(request, message_id):
    """
    Supprime un message (action modérateur).
    """
    message = get_object_or_404(Message, id=message_id)
    group_id = message.group.id
    message.delete()
    return redirect(f'/forum/?group_id={group_id}')

@login_required
def forum_home(request):
    """
    Vue principale du Forum (anciennement Social + News).
    Affiche le Chat, les Events, et la barre de Stories.
    """
    groups = Group.objects.all()
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    
    # Permission Check
    can_post_story = request.user.is_authenticated and (
        request.user.role_admin or 
        request.user.role_moderator or 
        request.user.is_staff or
        request.user.is_superuser
    )

    # 1. Chat Logic
    active_group = None
    messages = []
    
    group_id = request.GET.get('group_id')
    if group_id:
        active_group = get_object_or_404(Group, id=group_id)
        messages = active_group.messages.select_related('sender').all()
        
    if request.method == 'POST':
        # 2. Stories Upload Logic
        if 'story_image' in request.FILES:
            if can_post_story:
                target_group_id = request.POST.get('target_group_id')
                target_group = None
                if target_group_id:
                    target_group = get_object_or_404(Group, id=target_group_id)
                    
                Story.objects.create(
                    user=request.user,
                    image=request.FILES['story_image'],
                    group=target_group
                )
            return redirect('social:forum_home')
            
        # 3. Chat Logic
        elif active_group and 'content' in request.POST:
            content = request.POST.get('content')
            if content:
                Message.objects.create(
                    group=active_group,
                    sender=request.user,
                    content=content
                )
            return redirect(f'/forum/?group_id={active_group.id}')

    # 4. Fetch Active Stories & Group by Group
    now = timezone.now()
    # Only get stories that have a group, since we are moving to group-centric
    active_stories_qs = Story.objects.filter(expires_at__gt=now, group__isnull=False).select_related('group').order_by('-created_at')
    
    # Group by Group to show unique bubbles (deduplication)
    seen_groups = set()
    story_groups = []
    for story in active_stories_qs:
        if story.group.id not in seen_groups:
            story_groups.append(story.group)
            seen_groups.add(story.group.id)

    # 5. Determine Active Mode (Priority: Story > Group > Event > Default)
    active_mode = 'default'
    active_story_group = None
    active_event = None
    
    story_group_id = request.GET.get('story_group_id')
    event_id = request.GET.get('event_id')
    
    if story_group_id:
        active_mode = 'story'
        active_story_group = get_object_or_404(Group, id=story_group_id)
        # Filter stories for this specific group
        active_group_stories = Story.objects.filter(group=active_story_group, expires_at__gt=now).order_by('created_at')
    elif active_group:
        active_mode = 'chat'
    elif event_id:
        active_mode = 'event'
        active_event = get_object_or_404(Event, id=event_id)

    context = {
        'groups': groups,
        'events': events,
        'active_group': active_group,
        'messages': messages,
        'story_groups': story_groups,
        'active_mode': active_mode,
        'active_story_group': active_story_group,
        'active_group_stories': active_group_stories if active_mode == 'story' else None,
        'active_event': active_event,
        'can_post_story': can_post_story,
        'STATIC_VERSION': settings.STATIC_VERSION,
    }
    return render(request, 'social/forum.html', context)


# ========== FRIENDSHIP VIEWS (Phase 2.5.2) ==========

@login_required
def send_friend_request(request, user_id):
    """
    Envoyer une demande d'amitié à un utilisateur.
    """
    from .models import Friendship
    from django.contrib import messages
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    receiver = get_object_or_404(User, id=user_id)
    
    # Validation: Cannot friend yourself
    if receiver == request.user:
        return JsonResponse({'success': False, 'error': 'Vous ne pouvez pas vous ajouter vous-même'}, status=400)
    
    # Check if already friends
    if request.user.is_friend_with(receiver):
        return JsonResponse({'success': False, 'error': 'Vous êtes déjà amis'}, status=400)
    
    # Check if request already exists (in either direction)
    existing_request = Friendship.objects.filter(
        models.Q(requester=request.user, receiver=receiver) |
        models.Q(requester=receiver, receiver=request.user)
    ).first()
    
    if existing_request:
        return JsonResponse({'success': False, 'error': 'Une demande existe déjà'}, status=400)
    
    # Create friend request
    Friendship.objects.create(
        requester=request.user,
        receiver=receiver,
        status='pending'
    )
    
    return JsonResponse({'success': True, 'message': 'Demande envoyée'})


@login_required
def accept_friend_request(request, request_id):
    """
    Accepter une demande d'amitié.
    """
    from .models import Friendship
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    friendship = get_object_or_404(Friendship, id=request_id, receiver=request.user, status='pending')
    friendship.accept()
    
    return JsonResponse({'success': True, 'message': f'Vous êtes maintenant ami avec {friendship.requester.nickname}'})


@login_required
def reject_friend_request(request, request_id):
    """
    Rejeter ou annuler une demande d'amitié.
    """
    from .models import Friendship
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    # Can reject if you're the receiver, or cancel if you're the requester
    friendship = get_object_or_404(
        Friendship,
        id=request_id,
        status='pending'
    )
    
    # Validate user can perform this action
    if friendship.receiver != request.user and friendship.requester != request.user:
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)
    
    friendship.delete()
    
    return JsonResponse({'success': True, 'message': 'Demande supprimée'})


@login_required
def remove_friend(request, user_id):
    """
    Retirer un ami (supprimer l'amitié).
    """
    from .models import Friendship
    from django.http import JsonResponse
    from django.db.models import Q
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    other_user = get_object_or_404(User, id=user_id)
    
    # Find the friendship (could be in either direction)
    friendship = Friendship.objects.filter(
        Q(requester=request.user, receiver=other_user, status='accepted') |
        Q(requester=other_user, receiver=request.user, status='accepted')
    ).first()
    
    if not friendship:
        return JsonResponse({'success': False, 'error': 'Amitié non trouvée'}, status=404)
    
    friendship.delete()
    
    return JsonResponse({'success': True, 'message': f'{other_user.nickname} retiré de vos amis'})


@login_required
def friend_list(request, user_id=None):
    """
    Retourner la liste des amis d'un utilisateur (JSON pour AJAX).
    Si user_id est None, retourne les amis de l'utilisateur connecté.
    """
    from django.http import JsonResponse
    
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        user = request.user
    
    friends = user.get_friends()
    friends_data = [
        {
            'id': friend.id,
            'nickname': friend.nickname,
            'avatar': friend.avatar.url if friend.avatar else None,
            'level': friend.level,
        }
        for friend in friends
    ]
    
    return JsonResponse({
        'success': True,
        'friends': friends_data,
        'count': len(friends_data)
    })


# ========== SOCIAL DISCOVERY VIEWS (Phase 2.5.2.1) ==========

@login_required
def user_search_view(request):
    """
    Search and discover users with filters.
    Phase 2.5.2.1 - Social Discovery
    """
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    query = request.GET.get('q', '').strip()
    min_level = request.GET.get('min_level', '')
    max_level = request.GET.get('max_level', '')
    
    # Start with all users except current user
    users = User.objects.exclude(id=request.user.id)
    
    # Apply search query (nickname)
    if query:
        users = users.filter(
            Q(nickname__icontains=query)
        )
    
    # Apply level filters
    if min_level:
        try:
            users = users.filter(level__gte=int(min_level))
        except ValueError:
            pass
    
    if max_level:
        try:
            users = users.filter(level__lte=int(max_level))
        except ValueError:
            pass
    
    # Order by XP (highest first)
    users = users.order_by('-xp', '-level')
    
    # Pagination (20 users per page)
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'min_level': min_level,
        'max_level': max_level,
        'total_results': paginator.count,
    }
    
    return render(request, 'social/user_search.html', context)

