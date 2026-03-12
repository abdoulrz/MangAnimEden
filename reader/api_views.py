from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import ReadingProgress
from catalog.models import Chapter
import json

@login_required
@require_POST
def update_progress(request):
    """
    Met à jour la progression de lecture (page actuelle).
    Si l'utilisateur arrive à la dernière page, marque le chapitre comme terminé.
    XP est attribué via signal si 'completed' passe à True.
    """
    try:
        data = json.loads(request.body)
        chapter_id = data.get('chapter_id')
        page = int(data.get('page', 1))
        
        if not chapter_id:
            return JsonResponse({'success': False, 'error': 'chapter_id requis'}, status=400)
            
        chapter = get_object_or_404(Chapter, id=chapter_id)
        progress, created = ReadingProgress.objects.get_or_create(
            user=request.user,
            chapter=chapter
        )
        
        # On ne recule pas la progression dans la base de données pour le "Continue Reading" 
        # (Sauf si on veut vraiment suivre la position exacte en temps réel)
        # Mais ici, on va suivre la position exacte pour que "Reprendre lecture" soit précis.
        progress.current_page = page
        
        # Déterminer si terminé
        # On récupère le nombre total de pages
        total_pages = chapter.pages.count()
        
        was_completed = progress.completed
        if not was_completed and total_pages > 0 and page >= total_pages:
            progress.completed = True
            progress.save(update_fields=['current_page', 'completed', 'last_read'])
        else:
            progress.save(update_fields=['current_page', 'last_read'])
        
        return JsonResponse({
            'success': True,
            'completed': progress.completed,
            'current_page': progress.current_page,
            'total_pages': total_pages
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
