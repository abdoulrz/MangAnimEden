from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Group, Event, Message, Story
from django.contrib.auth import get_user_model
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
            return redirect('forum_home')
            
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
