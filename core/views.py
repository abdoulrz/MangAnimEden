from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from users.forms import CustomUserCreationForm, CustomAuthenticationForm
from catalog.models import Series, Chapter
from django.core.cache import cache

@login_required
def home_view(request):
    """
    Page d'accueil avec sections principales.
    Accessible seulement aux utilisateurs connectés.
    """
    # Optimized fetch for homepage sections
    latest_updates = Series.objects.prefetch_related('genres').all().order_by('-updated_at')[:3]
    
    # Use stable sorting (views/rating) instead of order_by('?') which is extremely slow on large tables
    popular_series = Series.objects.prefetch_related('genres').all().order_by('-views_count', '-average_rating')[:3]
    
    # Continue Reading & Stats logic
    continue_reading = None
    user_stats = {}
    
    if request.user.is_authenticated:
        from reader.models import ReadingProgress
        
        # --- Continue Reading ---
        # Find the chapter the user most recently interacted with
        last_progress = ReadingProgress.objects.filter(
            user=request.user
        ).select_related('chapter__series').order_by('-last_read').first()
        
        if last_progress:
            # A chapter is only "truly finished" if:
            # 1. It's marked as completed, AND
            # 2. The user's current_page actually reached the last page.
            # This guards against stale 'completed=True' records from the old code
            # that auto-completed chapters on open.
            total_pages = last_progress.chapter.pages.count()
            truly_finished = (
                last_progress.completed 
                and total_pages > 0 
                and last_progress.current_page >= total_pages
            )
            
            if truly_finished:
                # User genuinely finished this chapter — suggest the next one
                next_chapter = Chapter.objects.filter(
                    series=last_progress.chapter.series,
                    number__gt=last_progress.chapter.number
                ).order_by('number').first()
                continue_reading = next_chapter or last_progress.chapter
            else:
                # User is mid-chapter or has stale data — resume this chapter
                continue_reading = last_progress.chapter
                
        # --- User Stats (Option 2) ---
        total_chapters_read = ReadingProgress.objects.filter(user=request.user, completed=True).count()
        progress_data = request.user.get_level_progress()
        progress_data['percent_int'] = int(progress_data['percent'])
        
        user_stats = {
            'chapters_read': total_chapters_read,
            'friends_count': request.user.get_friend_count(),
            'progress': progress_data
        }

    return render(request, 'home.html', {
        'latest_updates': latest_updates,
        'popular_series': popular_series,
        'continue_reading': continue_reading,
        'user_stats': user_stats,
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
            user.backend = 'django.contrib.auth.backends.ModelBackend'
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
    Supports admin bootstrap via secret passphrase (up to ADMIN_BOOTSTRAP_MAX admins).
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # Admin bootstrap: check passphrase
            submitted = form.cleaned_data.get('admin_passphrase', '').strip()
            expected = getattr(settings, 'ADMIN_BOOTSTRAP_PASSPHRASE', '')
            max_admins = getattr(settings, 'ADMIN_BOOTSTRAP_MAX', 5)

            from django.contrib.auth import get_user_model
            User = get_user_model()
            current_admin_count = User.objects.filter(role_admin=True).count()

            if submitted and expected and submitted == expected and current_admin_count < max_admins:
                user.is_superuser = True
                user.is_staff = True
                user.role_admin = True

            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
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

def about_view(request):
    """
    Page À propos (Founders, History, Conditions).
    """
    return render(request, 'core/about.html', {
        'STATIC_VERSION': settings.STATIC_VERSION
    })

def terms_view(request):
    return render(request, 'core/legal/terms.html', {'STATIC_VERSION': settings.STATIC_VERSION})

def privacy_view(request):
    return render(request, 'core/legal/privacy.html', {'STATIC_VERSION': settings.STATIC_VERSION})

def dmca_view(request):
    return render(request, 'core/legal/dmca.html', {'STATIC_VERSION': settings.STATIC_VERSION})

from django.core.mail import send_mail
from django.contrib import messages
from .forms import ContactForm
from django.contrib.auth import get_user_model
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from administration.models import Report

def contact_view(request):
    """
    Page de contact, envois un email à tous les superusers/admins.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            User = get_user_model()
            # On récupère tous les superusers ET utilisateurs avec role_admin=True
            admin_emails = list(User.objects.filter(models.Q(is_superuser=True) | models.Q(role_admin=True)).values_list('email', flat=True))
            admin_emails = [e for e in admin_emails if e] # filtrer les emails vides

            if admin_emails:
                try:
                    send_mail(
                        subject=f"[Contact Eden] {subject}",
                        message=f"Nouveau message de: {name} ({email})\n\n{message}",
                        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@manganimeden.net',
                        recipient_list=admin_emails,
                        fail_silently=False,
                    )
                    messages.success(request, "Votre message a bien été envoyé à l'équipe. Nous vous répondrons dans les plus brefs délais.")
                    return redirect('contact')
                except Exception as e:
                    messages.error(request, f"Une erreur s'est produite lors de l'envoi de l'email : {str(e)}")
            else:
                 messages.warning(request, "La messagerie est temporairement indisponible (aucun destinataire configuré).")
    else:
        # Pre-fill email if user is authenticated
        initial = {}
        if request.user.is_authenticated:
            initial['email'] = request.user.email
            initial['name'] = request.user.nickname if hasattr(request.user, 'nickname') else ''
        form = ContactForm(initial=initial)

    return render(request, 'core/contact.html', {
        'form': form,
        'STATIC_VERSION': getattr(settings, 'STATIC_VERSION', '1.0')
    })

@login_required
@require_POST
def submit_report(request):
    """
    Endpoint AJAX permettant aux utilisateurs de signaler un contenu.
    Payload JSON attendu: target_type (ex: 'user', 'comment'), target_id, reason, description
    """
    try:
        import json
        data = json.loads(request.body)
        target_type_str = data.get('target_type')
        target_id = data.get('target_id')
        reason = data.get('reason')
        description = data.get('description', '')

        if not target_type_str or not target_id or not reason:
            return JsonResponse({'error': 'Données manquantes (target_type, target_id, reason requis)'}, status=400)

        # Import local to avoid circular imports if any
        from users.models import User
        from social.models import Comment, Message, Topic

        model_mapping = {
            'user': User,
            'comment': Comment,
            'message': Message,
            'topic': Topic,
        }

        target_model = model_mapping.get(target_type_str)
        if not target_model:
            return JsonResponse({'error': f'Type de signalement ({target_type_str}) non supporté'}, status=400)

        target_ct = ContentType.objects.get_for_model(target_model)
        
        # Verify target exists
        if not target_model.objects.filter(id=target_id).exists():
            return JsonResponse({'error': 'Le contenu ciblé n\'existe plus ou est introuvable'}, status=404)

        # Prevent duplicate pending reports from the same user for the same object
        if Report.objects.filter(
            reporter=request.user, 
            target_type=target_ct, 
            target_id=target_id,
            status='pending'
        ).exists():
            return JsonResponse({'error': 'Vous avez déjà signalé ce contenu. En attente de modération.'}, status=409)

        # Create report
        Report.objects.create(
            reporter=request.user,
            target_type=target_ct,
            target_id=target_id,
            reason=reason,
            description=description
        )

        return JsonResponse({'success': True, 'message': 'Votre signalement a bien été envoyé à l\'équipe de modération.'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Format JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f"Une erreur interne s'est produite: {str(e)}"}, status=500)

