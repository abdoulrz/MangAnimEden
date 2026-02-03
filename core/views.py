from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from users.forms import CustomUserCreationForm, CustomAuthenticationForm
from catalog.models import Series

@login_required
def home_view(request):
    """
    Page d'accueil avec sections principales.
    Accessible seulement aux utilisateurs connectés.
    """
    # Fetch series for the homepage
    latest_updates = Series.objects.all().order_by('-updated_at')[:3]
    popular_series = Series.objects.all().order_by('?')[:3] # Random for now as popular

    return render(request, 'home.html', {
        'latest_updates': latest_updates,
        'popular_series': popular_series,
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


@login_required
def news_view(request):
    """
    Page d'actualités avec les stories.
    """
    return render(request, 'news.html', {
        'STATIC_VERSION': settings.STATIC_VERSION
    })
