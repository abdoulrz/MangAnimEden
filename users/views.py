from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import UserUpdateForm

@login_required
def profile_view(request):
    """
    Vue du profil utilisateur.
    """
    return render(request, 'users/profile.html', {
        'STATIC_VERSION': settings.STATIC_VERSION
    })

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
