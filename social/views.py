from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Group, Event, Message
from django.utils import timezone

@login_required
def chat_home(request):
    groups = Group.objects.all()
    events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    
    active_group = None
    messages = []
    
    group_id = request.GET.get('group_id')
    if group_id:
        active_group = get_object_or_404(Group, id=group_id)
        messages = active_group.messages.select_related('sender').all()
        
    if request.method == 'POST' and active_group:
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                group=active_group,
                sender=request.user,
                content=content
            )
            return redirect(f'/social/?group_id={active_group.id}')

    stories = [
        {'name': 'Votre story', 'is_add': True},
        {'name': 'OnePiece...', 'color': 'has-story'},
        {'name': 'JJKNews', 'color': 'has-story'},
        {'name': 'MangaD...', 'color': 'has-story'},
        {'name': 'AnimeClub', 'color': 'has-story'},
        {'name': 'Otaku', 'color': 'has-story'},
    ]

    context = {
        'groups': groups,
        'events': events,
        'active_group': active_group,
        'messages': messages,
        'stories': stories,
    }
    return render(request, 'social/chat.html', context)
