from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Group, Event, Message, Story, GroupMembership
from .forms import GroupCreateForm, EventCreateForm
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
def delete_event(request, event_id):
    """
    Supprime un événement.
    Uniquement accessible aux Yonko Commander (niv 65+) ou staff/modos.
    """
    event = get_object_or_404(Event, id=event_id)
    
    # Strictly Level 65+ (including organizers) OR Moderator/Staff
    can_manage = (
        request.user.level >= 65 or 
        request.user.role_moderator or 
        request.user.role_admin or 
        request.user.is_staff
    )
    
    if not can_manage:
        messages.error(request, "Seuls les Yonko Commander (Niv. 65+) peuvent gérer les événements.")
        return redirect('social:forum_home')
        
    title = event.title
    event.delete()
    messages.success(request, f"L'événement '{title}' a été supprimé.")
    return redirect('social:forum_home')

@login_required
def join_group(request, group_id):
    """
    Rejoindre un groupe public.
    """
    group = get_object_or_404(Group, id=group_id)
    
    # Check if already member
    if GroupMembership.objects.filter(group=group, user=request.user).exists():
        messages.warning(request, "Vous êtes déjà membre de ce groupe.")
    else:
        GroupMembership.objects.create(group=group, user=request.user)
        messages.success(request, f"Vous avez rejoint le groupe {group.name} !")
        
    return redirect(f'/forum/?group_id={group.id}')

@login_required
def leave_group(request, group_id):
    """
    Quitter un groupe.
    """
    group = get_object_or_404(Group, id=group_id)
    
    # Check if owner (cannot leave without transfer)
    if group.owner == request.user:
        messages.error(request, "Le propriétaire ne peut pas quitter le groupe. Transférez la propriété ou supprimez le groupe.")
        return redirect(f'/forum/?group_id={group.id}')

    membership = GroupMembership.objects.filter(group=group, user=request.user).first()
    if membership:
        membership.delete()
        messages.success(request, f"Vous avez quitté le groupe {group.name}.")
    
    return redirect('social:forum_home')

@login_required
def forum_home(request):
    """
    Vue principale du Forum (anciennement Social + News).
    Affiche le Chat, les Events, et la barre de Stories.
    Updated for Phase 2.4.3: My Groups / Discover tabs.
    """
    from django.db.models import Q
    
    # 0. Get Tabs & Search
    active_tab = request.GET.get('tab', 'my_groups') # 'my_groups' or 'discover'
    search_query = request.GET.get('q', '')

    # 1. Fetch Groups based on membership
    my_memberships = GroupMembership.objects.filter(user=request.user).select_related('group')
    my_group_ids = my_memberships.values_list('group_id', flat=True)
    
    my_groups = Group.objects.filter(id__in=my_group_ids)
    other_groups = Group.objects.exclude(id__in=my_group_ids)

    # Search Filter
    if search_query:
        my_groups = my_groups.filter(name__icontains=search_query)
        other_groups = other_groups.filter(name__icontains=search_query)

    # --- Unified Sidebar Logic (DMs & Groupes) ---
    # 1. Fetch DM partners (Users I've exchanged messages with)
    from .models import DirectMessage
    sent_dms = DirectMessage.objects.filter(sender=request.user).values_list('recipient_id', flat=True)
    received_dms = DirectMessage.objects.filter(recipient=request.user).values_list('sender_id', flat=True)
    dm_user_ids = set(list(sent_dms) + list(received_dms))
    dm_partners = User.objects.filter(id__in=dm_user_ids)

    # 1.5 Fetch actual Friends for the dropdown
    friends = request.user.get_friends()[:50] # Limit for performance

    # 2. Build Sidebar List (Groups + DMs + Events)
    sidebar_items = []
    
    # Add Groups
    from django.db.models import Max
    for g in my_groups:
        latest_msg = Message.objects.filter(group=g).aggregate(Max('timestamp'))['timestamp__max']
        sidebar_items.append({
            'type': 'group',
            'id': g.id,
            'name': g.name,
            'avatar': g.icon.url if g.icon else None,
            'last_activity': latest_msg or g.created_at,
            'unread': False, # Placeholder
        })

    # Add DMs
    for u in dm_partners:
        latest_dm = DirectMessage.objects.filter(
            Q(sender=request.user, recipient=u) | Q(sender=u, recipient=request.user)
        ).aggregate(Max('timestamp'))['timestamp__max']
        sidebar_items.append({
            'type': 'dm',
            'id': u.id,
            'name': u.nickname or u.username,
            'avatar': u.avatar.url if u.avatar else None,
            'last_activity': latest_dm or timezone.now(),
            'is_online': u.is_online,
            'unread': DirectMessage.objects.filter(sender=u, recipient=request.user, is_read=False).exists(),
        })

    # Add Events (Upcoming)
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    for e in upcoming_events:
        sidebar_items.append({
            'type': 'event',
            'id': e.id,
            'name': e.title,
            'avatar': e.image.url if e.image else None,
            'last_activity': e.date, # Use date for proximity sorting
            'location': e.location,
            'unread': False,
        })

    # 3. Sort by LIFO
    sidebar_items.sort(key=lambda x: x['last_activity'], reverse=True)

    # Events
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    
    # Event Management Permission (Yonko Commander Niv. 65+)
    can_create_event = request.user.is_authenticated and (
        request.user.level >= 65 or 
        request.user.role_moderator or 
        request.user.role_admin or 
        request.user.is_staff
    )
    
    # Permission Check for Stories
    can_post_story = request.user.is_authenticated and (
        request.user.role_admin or 
        request.user.role_moderator or 
        request.user.is_staff or
        request.user.is_superuser or
        Group.objects.filter(owner=request.user).exists() # Group owners can post stories too? Let's keep it strict for now as per previous logic, or expand.
    )

    # 2. Chat Logic
    active_group = None
    messages_list = []
    is_member = False
    is_banned = False
    membership = None
    
    group_id = request.GET.get('group_id')
    if group_id:
        active_group = get_object_or_404(Group, id=group_id)
        
        # Check membership status
        membership = GroupMembership.objects.filter(group=active_group, user=request.user).first()
        if membership:
            is_member = True
            is_banned = membership.is_banned
            
        # Permission to view messages: Owners, Mods, or Members (if not banned)
        # Assuming public groups for now -> actually user request says "Should only see in the forum, the groups he is member of"
        # So we restrict message viewing to members only.
        if is_member and not is_banned:
            messages_list = active_group.messages.select_related('sender').all()
        elif request.user.is_staff or request.user.role_moderator or active_group.owner == request.user:
             # Staff/Mods/Owner can always see
             messages_list = active_group.messages.select_related('sender').all()

        # Phase 2.4.3 FIX: If viewing a group I'm not in, switch tab to 'discover'
        # unless I am the owner (then it's effectively my group)
        if not is_member and active_group.owner != request.user:
            active_tab = 'discover'
        
    if request.method == 'POST':
        # 3. Stories Upload Logic
        if 'story_image' in request.FILES or 'story_text' in request.POST:
            if can_post_story:
                target_group_id = request.POST.get('target_group_id')
                target_group = None
                if target_group_id:
                    target_group = get_object_or_404(Group, id=target_group_id)

                # Text Story
                if 'story_text' in request.POST and request.POST.get('story_text', '').strip():
                    Story.objects.create(
                        user=request.user,
                        group=target_group,
                        node_type='text',
                        text_content=request.POST['story_text'],
                        background_color=request.POST.get('story_bg_color', '#6c5ce7'),
                    )
                # Media Story
                elif 'story_image' in request.FILES:
                    uploaded = request.FILES['story_image']

                    # Magic bytes validation
                    valid_image = True
                    try:
                        import magic
                        file_mime = magic.from_buffer(uploaded.read(2048), mime=True)
                        uploaded.seek(0)  # Reset after reading
                        if not file_mime.startswith('image/'):
                            valid_image = False
                    except ImportError:
                        pass  # python-magic not installed, skip validation

                    if valid_image:
                        story = Story.objects.create(
                            user=request.user,
                            image=uploaded,
                            group=target_group,
                            node_type='media',
                        )
                        # Dispatch async media optimization
                        try:
                            from social.tasks import task_process_story_media
                            task_process_story_media.delay(story.id)
                        except Exception:
                            pass  # If Celery unavailable, image is saved as-is
            return redirect('social:forum_home')
            
        # 3.5 Event Creation Logic
        elif 'event_title' in request.POST:
            if can_create_event:
                form = EventCreateForm(request.POST, request.FILES)
                if form.is_valid():
                    event = form.save(commit=False)
                    event.organizer = request.user
                    event.save()
                    messages.success(request, f"L'événement '{event.title}' a été créé !")
            return redirect('social:forum_home')
            
        # 4. Chat Logic (Post Message)
        elif (active_group or 'dm_id' in request.POST) and 'content' in request.POST:
            content = request.POST.get('content')
            
            if 'dm_id' in request.POST:
                recipient_id = request.POST.get('dm_id')
                recipient = get_object_or_404(User, id=recipient_id)
                
                # Verify friendship
                if not request.user.is_friend_with(recipient):
                    messages.error(request, "Vous devez être amis pour envoyer des messages privés.")
                    return redirect('social:forum_home')
                
                dm = DirectMessage.objects.create(
                    sender=request.user,
                    recipient=recipient,
                    content=content
                )
                
                # Notification for DM
                from .services import NotificationService
                NotificationService.create_notification(
                    recipient=recipient,
                    actor=request.user,
                    verb="vous a envoyé un message privé",
                    type='message',
                    target=dm
                )
                return redirect(f'/forum/?dm_id={recipient.id}')

            # Group Message Logic (unchanged but wrapped)
            # Security check: Must be member and not banned
            if not is_member and not (request.user.is_staff or request.user.role_moderator or active_group.owner == request.user):
                 messages.error(request, "Vous devez rejoindre le groupe pour participer.")
                 return redirect(f'/forum/?group_id={active_group.id}')
            
            if is_banned:
                messages.error(request, "Vous êtes banni de ce groupe.")
                return redirect(f'/forum/?group_id={active_group.id}')

            parent_id = request.POST.get('parent_id')
            parent_message = None
            
            if parent_id:
                try:
                    parent_message = Message.objects.get(id=parent_id)
                except Message.DoesNotExist:
                    pass
            
            if content:
                msg = Message.objects.create(
                    group=active_group,
                    sender=request.user,
                    content=content,
                    parent=parent_message
                )
                
                # Notification: Reply
                from .services import NotificationService
                if parent_message and parent_message.sender != request.user:
                    NotificationService.create_notification(
                        recipient=parent_message.sender,
                        actor=request.user,
                        verb="a répondu à votre message",
                        type='reply',
                        target=msg
                    )
            return redirect(f'/forum/?group_id={active_group.id}')

    # 5. Fetch Active Stories & Group by Group
    now = timezone.now()
    active_stories_qs = Story.objects.filter(expires_at__gt=now, group__isnull=False).select_related('group').order_by('-created_at')
    
    seen_groups = set()
    story_groups = []
    for story in active_stories_qs:
        if story.group.id not in seen_groups:
            story_groups.append(story.group)
            seen_groups.add(story.group.id)

    # 6. Determine Active Mode
    active_mode = 'default'
    active_story_group = None
    active_event = None
    active_dm_user = None
    
    story_group_id = request.GET.get('story_group_id')
    event_id = request.GET.get('event_id')
    dm_id = request.GET.get('dm_id')
    
    if story_group_id:
        active_mode = 'story'
        active_story_group = get_object_or_404(Group, id=story_group_id)
        active_group_stories = Story.objects.filter(group=active_story_group, expires_at__gt=now).order_by('created_at')
    elif dm_id:
        active_mode = 'dm'
        active_dm_user = get_object_or_404(User, id=dm_id)
        # Verify friendship? Spec says only friends can DM.
        # Fetch DM history
        from .models import DirectMessage
        messages_list = DirectMessage.objects.filter(
            (Q(sender=request.user) & Q(recipient=active_dm_user)) |
            (Q(sender=active_dm_user) & Q(recipient=request.user))
        ).order_by('timestamp')
        # Mark as read
        DirectMessage.objects.filter(sender=active_dm_user, recipient=request.user, is_read=False).update(is_read=True)
    elif active_group:
        active_mode = 'chat'
    elif event_id:
        active_mode = 'event'
        active_event = get_object_or_404(Event, id=event_id)

    context = {
        'sidebar_items': sidebar_items,
        'my_groups': my_groups,
        'other_groups': other_groups,
        'active_tab': active_tab, 
        'events': events,
        'active_mode': active_mode,
        'active_group': active_group,
        'active_dm_user': active_dm_user,
        'messages_list': messages_list,
        'is_member': is_member,
        'is_banned': is_banned,
        'story_groups': story_groups,
        'active_story_group': active_story_group,
        'active_group_stories': active_group_stories if active_mode == 'story' else None,
        'active_event': active_event,
        'can_post_story': can_post_story,
        'can_create_event': can_create_event,
        'event_form': EventCreateForm(),
        'friends': friends,
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
    
    # Notification: Friend Request
    from .services import NotificationService
    NotificationService.create_notification(
        recipient=receiver,
        actor=request.user,
        verb="vous a envoyé une demande d'ami",
        type='friend_request'
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
    
    # Notification: Request Accepted (Notify the requester)
    from .services import NotificationService
    NotificationService.create_notification(
        recipient=friendship.requester,
        actor=request.user,
        verb="a accepté votre demande d'ami",
        type='friend_accept'
    )
    
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


# ========== GROUP MANAGEMENT (Phase 2.5.4 & 2.5.5) ==========

@login_required
def create_group(request):
    """
    Vue pour créer un nouveau groupe.
    Restreint aux utilisateurs de niveau >= 50 ou Modérateurs.
    """
    from .forms import GroupCreateForm
    from django.contrib import messages
    
    # 1. Level / Role Check
    is_privileged = request.user.is_staff or request.user.role_admin or request.user.role_moderator
    if request.user.level < 50 and not is_privileged:
        messages.error(request, "Vous devez atteindre le niveau 50 pour créer un groupe.")
        return redirect('social:forum_home')
        
    # 2. Quota Check
    owned_groups_count = Group.objects.filter(owner=request.user).count()
    max_allowed = request.user.level // 50
    if not is_privileged and owned_groups_count >= max_allowed:
        messages.error(request, f"Vous avez atteint la limite de création de groupes ({max_allowed}). Montez de niveau pour en créer plus !")
        return redirect('social:forum_home')

    if request.method == 'POST':
        form = GroupCreateForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            group.save()
            messages.success(request, f"Le groupe '{group.name}' a été créé avec succès !")
            return redirect('social:forum_home')
    else:
        form = GroupCreateForm()
    
    return render(request, 'social/group_create.html', {'form': form})


@login_required
def ban_user(request, group_id, user_id):
    """
    Vue pour bannir/débannir un utilisateur d'un groupe.
    Seul le propriétaire du groupe peut effectuer cette action.
    """
    from .models import GroupMembership
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
        
    group = get_object_or_404(Group, id=group_id)
    
    # Permission Check: Only Owner
    if group.owner != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Non autorisé'}, status=403)
        
    target_user = get_object_or_404(User, id=user_id)
    
    # Cannot ban owner
    if target_user == group.owner:
        return JsonResponse({'success': False, 'error': 'Impossible de bannir le propriétaire'}, status=400)
        
    membership, created = GroupMembership.objects.get_or_create(group=group, user=target_user)
    
    # Toggle Ban Status
    membership.is_banned = not membership.is_banned
    if membership.is_banned:
        membership.banned_at = timezone.now()
    else:
        membership.banned_at = None
    membership.save()
    
    action = "banni" if membership.is_banned else "débanni"
    return JsonResponse({'success': True, 'message': f"{target_user.nickname} a été {action} du groupe.", 'is_banned': membership.is_banned})


# ========== NOTIFICATION VIEWS (Phase 3.2.1) ==========

@login_required
def notifications_list(request):
    """
    Page affichant toutes les notifications de l'utilisateur.
    """
    from .models import Notification
    from .services import NotificationService
    
    # Check if user wants to mark specific notification as read via GET param (simple redirect implementation)
    # Ideally use AJAX for individual, but this is fallback
    notif_id = request.GET.get('read')
    if notif_id:
        NotificationService.mark_as_read(request.user, notif_id)
        return redirect('social:notifications_list')

    # Mark all as read logic
    if request.method == 'POST' and 'mark_all_read' in request.POST:
        NotificationService.mark_as_read(request.user) # Mark all
        messages.success(request, "Toutes les notifications ont été marquées comme lues.")
        return redirect('social:notifications_list')
        
    notifications = Notification.objects.filter(recipient=request.user).select_related('actor', 'content_type')
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'social/notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """
    Marque une notification spécifique comme lue (AJAX/HTMX).
    """
    from .services import NotificationService
    from django.http import JsonResponse
    
    if request.method == 'POST':
        NotificationService.mark_as_read(request.user, notification_id)
        return JsonResponse({'success': True})
        
    return JsonResponse({'success': False}, status=400)


@login_required
def like_message(request, message_id):
    """
    Toggle Like on a message.
    """
    from .models import Message
    from .services import NotificationService
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
        
    message = get_object_or_404(Message, id=message_id)
    
    if request.user in message.likes.all():
        message.likes.remove(request.user)
        liked = False
    else:
        message.likes.add(request.user)
        liked = True
        
        # Notification: Like
        if message.sender != request.user:
            NotificationService.create_notification(
                recipient=message.sender,
                actor=request.user,
                verb="a aimé votre message",
                type='like',
                target=message
            )
            
    return JsonResponse({
        'success': True, 
        'liked': liked, 
        'count': message.like_count
    })

@login_required
def reply_message(request, message_id):
    """
    Reply to a message.
    """
    from .models import Message
    from .services import NotificationService
    
    parent_message = get_object_or_404(Message, id=message_id)
    group_id = parent_message.group.id
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            reply = Message.objects.create(
                group=parent_message.group,
                sender=request.user,
                content=content,
                parent=parent_message
            )
            
            # Notification: Reply
            if parent_message.sender != request.user:
                NotificationService.create_notification(
                    recipient=parent_message.sender,
                    actor=request.user,
                    verb="a répondu à votre message",
                    type='reply',
                    target=reply
                )
                
    return redirect(f'/forum/?group_id={group_id}')
