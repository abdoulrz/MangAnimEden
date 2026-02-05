from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from users.forms import CustomUserCreationForm, CustomAuthenticationForm
from catalog.models import Series, Chapter
import requests
from django.core.cache import cache

@login_required
def home_view(request):
    """
    Page d'accueil avec sections principales.
    Accessible seulement aux utilisateurs connectés.
    """
    # Fetch series for the homepage
    latest_updates = Series.objects.all().order_by('-updated_at')[:3]
    popular_series = Series.objects.all().order_by('?')[:3] # Random for now as popular
    
    # Fetch anime quote from API (cached for 1 hour)
    quote_data = cache.get('anime_quote')
    if not quote_data:
        try:
            response = requests.get('https://animechan.xyz/api/random', timeout=5)
            if response.status_code == 200:
                quote_data = response.json()
                cache.set('anime_quote', quote_data, 3600)  # Cache for 1 hour
        except Exception:
            quote_data = None
    
    # Continue Reading logic
    continue_reading = None
    if request.user.is_authenticated:
        from reader.models import ReadingProgress
        
        last_progress = ReadingProgress.objects.filter(
            user=request.user
        ).select_related('chapter__series').order_by('-last_read').first()
        
        if last_progress:
            # If completed, get next chapter
            if last_progress.completed:
                next_chapter = Chapter.objects.filter(
                    series=last_progress.chapter.series,
                    number__gt=last_progress.chapter.number
                ).order_by('number').first()
                continue_reading = next_chapter or last_progress.chapter
            else:
                continue_reading = last_progress.chapter

    return render(request, 'home.html', {
        'latest_updates': latest_updates,
        'popular_series': popular_series,
        'quote': quote_data,
        'continue_reading': continue_reading,
        'STATIC_VERSION': settings.STATIC_VERSION
    })


def login_view(request):
    """
    Page de connexion utilisateur.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'auth/login.html', {
        'form': form,
        'STATIC_VERSION': settings.STATIC_VERSION
    })


def register_view(request):
    """
    Page d'inscription utilisateur.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'auth/register.html', {
        'form': form,
        'STATIC_VERSION': settings.STATIC_VERSION
    })

def logout_view(request):
    """
    Déconnexion de l'utilisateur.
    """
    logout(request)
    return redirect('login')



