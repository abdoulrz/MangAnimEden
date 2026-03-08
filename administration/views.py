import logging
import os
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView
from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from .decorators import requires_admin, requires_moderator, log_admin_action, create_system_log
from .models import SystemLog
from catalog.models import Series, Chapter, Genre
from social.models import Group  # Import Group model
from users.models import Badge

User = get_user_model()
logger = logging.getLogger(__name__)

@method_decorator(requires_admin, name='dispatch')
class AdminDashboardView(TemplateView):
    template_name = 'administration/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Key Metrics
        context['total_users'] = User.objects.count()
        context['new_users_today'] = User.objects.filter(date_joined__date=timezone.now().date()).count()
        context['total_series'] = Series.objects.count()
        context['total_chapters'] = Chapter.objects.count()
        context['total_groups'] = Group.objects.count()
        
        # Recent Activity (Logs)
        context['recent_logs'] = SystemLog.objects.select_related('actor', 'target_user').order_by('-created_at')[:10]
        
        # Pending Reports (Placeholder for future)
        context['pending_reports_count'] = 0
        
        context['active_tab'] = 'dashboard'
        return context

@method_decorator(requires_moderator, name='dispatch')
class UserManagementView(ListView):
    model = User
    template_name = 'administration/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    ordering = ['-date_joined']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(email__icontains=query) | 
                Q(nickname__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'users'
        return context

@method_decorator(requires_admin, name='dispatch')
class UserActionView(View):
    @method_decorator(log_admin_action('USER_ACTION')) # Generic action type, refined inside if needed
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        if not user_id or not action:
            messages.error(request, "Invalid request.")
            return redirect('administration:user_list')
            
        target_user = get_object_or_404(User, id=user_id)
        
        # Prevent self-lockout
        if target_user == request.user and action in ['toggle_admin', 'toggle_ban']:
            messages.error(request, "You cannot perform this action on yourself.")
            return redirect('administration:user_list')

        msg = ""
        if action == 'toggle_admin':
            target_user.role_admin = not target_user.role_admin
            msg = "Admin status updated."
        elif action == 'toggle_moderator':
            target_user.role_moderator = not target_user.role_moderator
            msg = "Moderator status updated."
        elif action == 'toggle_ban':
            target_user.is_banned = not target_user.is_banned
            target_user.is_active = not target_user.is_banned # Sync is_active
            msg = "Ban status updated."
        else:
            messages.error(request, "Unknown action.")
            return redirect('administration:user_list')
            
        target_user.save()
        messages.success(request, f"User {target_user.nickname}: {msg}")
        
        return redirect('administration:user_list')


# --- Content Management (Series) ---
@method_decorator(requires_admin, name='dispatch')
class AdminSeriesListView(ListView):
    model = Series
    template_name = 'administration/content/series_list.html'
    context_object_name = 'series_list'
    paginate_by = 20
    ordering = ['-updated_at']

    def get_queryset(self):
        queryset = super().get_queryset().annotate(chapter_count=Count('chapters'))
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'series'
        return context

from catalog.services import bulk_create_chapters_from_folder
from .forms import SeriesForm, BadgeForm

@method_decorator(requires_admin, name='dispatch')
class AdminSeriesCreateView(CreateView):
    model = Series
    form_class = SeriesForm
    template_name = 'administration/content/series_form.html'
    success_url = reverse_lazy('administration:series_list')

    def form_valid(self, form):
        self.object = form.save()
        create_system_log(self.request, 'SERIES_CREATE', details=f"Série créée : {self.object.title}")
        
        # If it's an AJAX request (for our iterative chunking flow)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'series_id': self.object.id,
                'message': 'Série créée avec succès.'
            })

        # Standard flow (backward compatibility) block removed to prevent OOMs
        # Only chunked uploads via JS are allowed for massive folders now.
            
        messages.success(self.request, "Série créée avec succès.")
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {field: errs.get_json_data() for field, errs in form.errors.items()}
            return JsonResponse({'error': 'Erreurs de validation', 'errors': errors}, status=400)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'series'
        return context

@method_decorator(requires_admin, name='dispatch')
class AdminSeriesUpdateView(UpdateView):
    model = Series
    form_class = SeriesForm
    template_name = 'administration/content/series_form.html'
    success_url = reverse_lazy('administration:series_list')

    def form_valid(self, form):
        self.object = form.save()
        create_system_log(self.request, 'SERIES_UPDATE', details=f"Série modifiée : {self.object.title}")
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'series_id': self.object.id,
                'message': 'Série mise à jour.'
            })

        # Standard flow (backward compatibility) block removed to prevent OOMs
        # Only chunked uploads via JS are allowed for massive folders now.

        messages.success(self.request, "Série mise à jour avec succès.")
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {field: errs.get_json_data() for field, errs in form.errors.items()}
            return JsonResponse({'error': 'Erreurs de validation', 'errors': errors}, status=400)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'series'
        return context

@method_decorator(requires_admin, name='dispatch')
class AdminSeriesDeleteView(DeleteView):
    model = Series
    success_url = reverse_lazy('administration:series_list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        create_system_log(request, 'SERIES_DELETE', details=f"Série supprimée : {obj.title}")
        messages.success(request, f"Série '{obj.title}' supprimée.")
        return super().delete(request, *args, **kwargs)


# --- Content Management (Chapters) ---
@method_decorator(requires_admin, name='dispatch')
class AdminChapterListView(ListView):
    model = Chapter
    template_name = 'administration/content/chapter_list.html'
    context_object_name = 'chapters'
    paginate_by = 500

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'series'
        series_id = self.kwargs.get('series_id')
        if series_id:
            context['current_series'] = get_object_or_404(Series, id=series_id)
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        series_id = self.kwargs.get('series_id')
        if series_id:
            qs = qs.filter(series_id=series_id)
        return qs.order_by('-number')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        series_id = self.kwargs.get('series_id')
        if series_id:
            context['current_series'] = get_object_or_404(Series, id=series_id)
        return context

from .forms import ChapterForm
from catalog.services import FileProcessor
import threading

@method_decorator(requires_admin, name='dispatch')
class AdminChapterCreateView(CreateView):
    model = Chapter
    form_class = ChapterForm
    template_name = 'administration/content/chapter_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        series_id = self.kwargs.get('series_id')
        if series_id:
            initial['series'] = series_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        series_id = self.kwargs.get('series_id')
        if series_id:
            context['current_series'] = get_object_or_404(Series, id=series_id)
        return context

    def get_success_url(self):
        return reverse_lazy('administration:chapter_list', kwargs={'series_id': self.object.series.id})

    def form_valid(self, form):
        uploaded_file = self.request.FILES.get('source_file')
        
        # Save the chapter WITHOUT the source_file to avoid uploading the huge archive to R2
        # (We only need the extracted page images on R2, not the raw CBZ/PDF)
        if uploaded_file:
            form.instance.source_file = None
        self.object = form.save()
        
        if uploaded_file:
            # Stream uploaded file to temp disk in chunks (never holds full file in RAM)
            import tempfile
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            temp_fd, temp_path = tempfile.mkstemp(suffix=ext)
            try:
                with os.fdopen(temp_fd, 'wb') as tmp:
                    for chunk in uploaded_file.chunks(chunk_size=2 * 1024 * 1024):  # 2MB chunks
                        tmp.write(chunk)
            except Exception:
                os.close(temp_fd)
                raise
            
            # Process in background — thread wraps Celery dispatch
            # (needed because CELERY_TASK_ALWAYS_EAGER makes .delay() synchronous)
            def _dispatch():
                from catalog.tasks import task_process_chapter
                task_process_chapter.delay(self.object.series.id, None, temp_path)
            threading.Thread(target=_dispatch, daemon=True).start()
            
        create_system_log(self.request, 'CHAPTER_CREATE', details=f"Chapitre créé : {self.object.number} pour {self.object.series.title}")
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': "Chapitre créé avec succès. Extraction des pages en cours...",
                'redirect_url': str(self.get_success_url()),
            })
        
        messages.success(self.request, "Chapitre créé avec succès. L'extraction des pages est en cours en arrière-plan.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {field: errs.get_json_data() for field, errs in form.errors.items()}
            return JsonResponse({'error': 'Erreurs de validation', 'errors': errors}, status=400)
        return super().form_invalid(form)

@method_decorator(requires_admin, name='dispatch')
class AdminChapterUpdateView(UpdateView):
    model = Chapter
    form_class = ChapterForm
    template_name = 'administration/content/chapter_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'series'
        # For update, we get the series from the object
        context['current_series'] = self.object.series
        return context

    def get_success_url(self):
        return reverse_lazy('administration:chapter_list', kwargs={'series_id': self.object.series.id})

    def form_valid(self, form):
        uploaded_file = self.request.FILES.get('source_file')
        
        # Clear source_file before saving to avoid uploading archive to R2
        if uploaded_file:
            form.instance.source_file = None
        self.object = form.save()
        
        # Process the file if a new one was uploaded
        if uploaded_file:
            self.object.pages.all().delete()
            
            # Stream uploaded file to temp disk in chunks
            import tempfile
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            temp_fd, temp_path = tempfile.mkstemp(suffix=ext, dir=settings.MEDIA_ROOT)
            try:
                with os.fdopen(temp_fd, 'wb') as tmp:
                    for chunk in uploaded_file.chunks(chunk_size=2 * 1024 * 1024):
                        tmp.write(chunk)
            except Exception:
                os.close(temp_fd)
                raise
            
            # Process in background — thread wraps Celery dispatch
            def _dispatch():
                from catalog.tasks import task_process_chapter
                task_process_chapter.delay(self.object.series.id, None, temp_path)
            threading.Thread(target=_dispatch, daemon=True).start()
            msg = "Chapitre mis à jour. Extraction des nouvelles pages en cours..."
        else:
            msg = "Chapitre mis à jour."
            
        create_system_log(self.request, 'CHAPTER_UPDATE', details=f"Chapitre modifié : {self.object.number} pour {self.object.series.title}")
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': msg,
                'redirect_url': str(self.get_success_url()),
            })
        
        messages.success(self.request, msg)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {field: errs.get_json_data() for field, errs in form.errors.items()}
            return JsonResponse({'error': 'Erreurs de validation', 'errors': errors}, status=400)
        return super().form_invalid(form)

@method_decorator(requires_admin, name='dispatch')
class AdminChapterDeleteView(DeleteView):
    model = Chapter
    
    def get_success_url(self):
        return reverse_lazy('administration:chapter_list', kwargs={'series_id': self.object.series.id})
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        create_system_log(request, 'CHAPTER_DELETE', details=f"Chapitre supprimé : {obj.number} de {obj.series.title}")
        messages.success(request, f"Chapitre {obj.number} supprimé.")
        return super().delete(request, *args, **kwargs)


# --- Content Management (Genres) ---
@method_decorator(requires_admin, name='dispatch')
class AdminGenreListView(ListView):
    model = Genre
    template_name = 'administration/content/genre_list.html'
    context_object_name = 'genres'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'genres'
        return context

@method_decorator(requires_admin, name='dispatch')
class AdminGenreCreateView(CreateView):
    model = Genre
    template_name = 'administration/content/genre_form.html'
    fields = ['name', 'slug']
    success_url = reverse_lazy('administration:genre_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        create_system_log(self.request, 'GENRE_CREATE', details=f"Genre créé : {self.object.name}")
        messages.success(self.request, "Genre créé avec succès.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'genres'
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'genres'
        return context

@method_decorator(requires_admin, name='dispatch')
class AdminGenreUpdateView(UpdateView):
    model = Genre
    template_name = 'administration/content/genre_form.html'
    fields = ['name', 'slug']
    success_url = reverse_lazy('administration:genre_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        create_system_log(self.request, 'GENRE_UPDATE', details=f"Genre modifié : {self.object.name}")
        messages.success(self.request, "Genre mis à jour avec succès.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'genres'
        return context

@method_decorator(requires_admin, name='dispatch')
class AdminGenreDeleteView(DeleteView):
    model = Genre
    success_url = reverse_lazy('administration:genre_list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        create_system_log(request, 'GENRE_DELETE', details=f"Genre supprimé : {obj.name}")
        messages.success(request, f"Genre '{obj.name}' supprimé.")
        return super().delete(request, *args, **kwargs)


# --- Community Management (Groups) ---
@method_decorator(requires_moderator, name='dispatch')
class AdminGroupListView(ListView):
    model = Group
    template_name = 'administration/community/group_list.html'
    context_object_name = 'groups'
    paginate_by = 20
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'groups'
        return context

@method_decorator(requires_moderator, name='dispatch')
class AdminGroupUpdateView(UpdateView):
    model = Group
    template_name = 'administration/community/group_form.html'
    fields = ['name', 'description', 'icon'] # Add status field if available, for now just basic edit
    success_url = reverse_lazy('administration:group_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'groups'
        return context
    
    # Note: Banning/Closing logic is ideally a dedicated action view like UserActionView
    # But for MVP, simple edit access allows cleaning description/name.

    def form_valid(self, form):
        response = super().form_valid(form)
        create_system_log(self.request, 'GROUP_UPDATE', details=f"Groupe modifié : {self.object.name}")
        messages.success(self.request, "Groupe mis à jour avec succès.")
        return response

@method_decorator(requires_moderator, name='dispatch')
class AdminGroupDeleteView(DeleteView):
    model = Group
    success_url = reverse_lazy('administration:group_list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        create_system_log(request, 'GROUP_DELETE', details=f"Groupe supprimé : {obj.name}")
        messages.success(request, f"Groupe '{obj.name}' supprimé.")
        return super().delete(request, *args, **kwargs)

from django.http import JsonResponse
from .models import ChunkedUpload
from .upload_service import ChunkedUploadService

@method_decorator(requires_admin, name='dispatch')
class InitChunkedUploadView(View):
    def post(self, request, *args, **kwargs):
        filename = request.POST.get('filename')
        total_chunks = request.POST.get('total_chunks')
        
        if not filename or not total_chunks:
            return JsonResponse({'error': 'Missing parameters'}, status=400)
            
        upload = ChunkedUpload.objects.create(
            user=request.user,
            filename=filename,
            total_chunks=int(total_chunks)
        )
        
        return JsonResponse({
            'upload_id': str(upload.upload_id),
            'status': 'initiated'
        })

@method_decorator(requires_admin, name='dispatch')
class UploadChunkView(View):
    def post(self, request, *args, **kwargs):
        upload_id = request.POST.get('upload_id')
        chunk_index = request.POST.get('chunk_index')
        chunk_file = request.FILES.get('chunk')
        
        if not upload_id or chunk_index is None or not chunk_file:
            return JsonResponse({'error': 'Missing parameters'}, status=400)
            
        try:
            ChunkedUploadService.save_chunk(upload_id, chunk_file, int(chunk_index))
            return JsonResponse({'status': 'chunk_saved'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(requires_admin, name='dispatch')
class CompleteChunkedUploadView(View):
    def post(self, request, *args, **kwargs):
        upload_id = request.POST.get('upload_id')
        
        if not upload_id:
            return JsonResponse({'error': 'Missing upload_id'}, status=400)
            
        try:
            final_path = ChunkedUploadService.assemble_file(upload_id)
            return JsonResponse({
                'status': 'completed',
                'final_path': final_path
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

from catalog.services import process_single_chapter_from_temp
import tempfile

def background_process_chapters(series_id, upload_ids):
    """Dispatch each chapter to a Celery task for processing."""
    from catalog.tasks import task_process_chapter
    from django.conf import settings
    import tempfile as tmpmod

    for upload_id in upload_ids:
        try:
            upload = ChunkedUpload.objects.get(upload_id=upload_id)
            base_dir = getattr(settings, 'MEDIA_ROOT', tmpmod.gettempdir())
            base_temp_dir = os.path.join(base_dir, 'manga_temp_uploads', str(upload_id))
            temp_path = os.path.join(base_temp_dir, os.path.basename(upload.filename))

            if not os.path.exists(temp_path):
                # Fallback purely in case it was stored without the upload_id directory
                fallback_dir = os.path.join(base_dir, 'manga_temp_uploads')
                temp_path = os.path.join(fallback_dir, os.path.basename(upload.filename))

            if os.path.exists(temp_path):
                task_process_chapter.delay(series_id, str(upload_id), temp_path)
            else:
                logger.error(f"Assembled file not found for upload {upload_id}")
                upload.status = 'failed'
                upload.save(update_fields=['status'])

        except Exception as e:
            logger.error(f"Error dispatching upload {upload_id}: {e}")
            try:
                upload = ChunkedUpload.objects.get(upload_id=upload_id)
                upload.status = 'failed'
                upload.save(update_fields=['status'])
            except ChunkedUpload.DoesNotExist:
                pass

@method_decorator(requires_admin, name='dispatch')
class ProcessChapterFromUploadView(View):
    def post(self, request, *args, **kwargs):
        upload_ids_str = request.POST.get('upload_ids')
        series_id = request.POST.get('series_id')
        
        if not upload_ids_str or not series_id:
            return JsonResponse({'error': 'Paramètres manquants'}, status=400)
            
        try:
            upload_ids = [uid.strip() for uid in upload_ids_str.split(',') if uid.strip()]
            
            if upload_ids:
                # Dispatch in a background thread so the HTTP response returns immediately
                # (CELERY_TASK_ALWAYS_EAGER makes .delay() synchronous, which would block)
                thread = threading.Thread(
                    target=background_process_chapters,
                    args=(series_id, upload_ids),
                    daemon=True
                )
                thread.start()
                
            return JsonResponse({
                'status': 'processing_started',
                'message': f"{len(upload_ids)} chapitres en cours de traitement en arrière-plan."
            })
        except Exception as e:
            logger.error(f"Error starting background processing: {e}")
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(requires_admin, name='dispatch')
class UploadProgressStatusView(View):
    def get(self, request, *args, **kwargs):
        from django.utils import timezone
        from datetime import timedelta
        
        upload_ids_str = request.GET.get('upload_ids', '')
        if not upload_ids_str:
            return JsonResponse({'error': 'Paramètres manquants'}, status=400)
            
        upload_ids = [uid.strip() for uid in upload_ids_str.split(',') if uid.strip()]
        
        try:
            uploads = ChunkedUpload.objects.filter(upload_id__in=upload_ids)
            stale_threshold = timezone.now() - timedelta(minutes=30)  # Match Celery hard limit
            
            stats = {
                'total_files': 0,
                'processed_files': 0,
                'terminal_uploads': 0,  # completed + failed + stale
                'total_uploads': len(upload_ids),
                'status': 'processing'
            }
            
            for upload in uploads:
                stats['total_files'] += upload.total_files_to_process
                stats['processed_files'] += upload.processed_files
                
                # Count terminal states: completed, failed, or stale
                if upload.status in ('completed', 'failed'):
                    stats['terminal_uploads'] += 1
                elif upload.status == 'uploading' and upload.created_at < stale_threshold:
                    # Only mark 'uploading' as stale (never 'processing' — task may still be working)
                    upload.status = 'failed'
                    upload.save(update_fields=['status'])
                    stats['terminal_uploads'] += 1
                elif upload.status == 'completed' and upload.processed_files >= upload.total_files_to_process and upload.total_files_to_process > 0:
                    stats['terminal_uploads'] += 1
                     
            if stats['total_files'] > 0:
                stats['percentage'] = round((stats['processed_files'] / stats['total_files']) * 100)
            else:
                stats['percentage'] = 0
                
            # Finished if: all uploads reached a terminal state, OR no records exist at all (deleted)
            if stats['terminal_uploads'] >= len(upload_ids) or uploads.count() == 0:
                stats['status'] = 'finished'
                
                # Check if any failed
                failed_count = uploads.filter(status='failed').count()
                if failed_count > 0:
                    stats['status'] = 'failed'
                    stats['message'] = f"{failed_count} upload(s) ont échoué."
                 
            return JsonResponse(stats)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# --- Gamification Management (Badges) ---
@method_decorator(requires_admin, name='dispatch')
class AdminBadgeListView(ListView):
    model = Badge
    template_name = 'administration/gamification/badge_list.html'
    context_object_name = 'badges'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'badges'
        return context

@method_decorator(requires_admin, name='dispatch')
class AdminBadgeCreateView(CreateView):
    model = Badge
    form_class = BadgeForm
    template_name = 'administration/gamification/badge_form.html'
    success_url = reverse_lazy('administration:badge_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        create_system_log(self.request, 'BADGE_CREATE', details=f"Badge créé : {self.object.name}")
        messages.success(self.request, "Badge créé avec succès.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'badges'
        return context

@method_decorator(requires_admin, name='dispatch')
class AdminBadgeUpdateView(UpdateView):
    model = Badge
    form_class = BadgeForm
    template_name = 'administration/gamification/badge_form.html'
    success_url = reverse_lazy('administration:badge_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        create_system_log(self.request, 'BADGE_UPDATE', details=f"Badge modifié : {self.object.name}")
        messages.success(self.request, "Badge mis à jour avec succès.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'badges'
        return context

@method_decorator(requires_admin, name='dispatch')
class AdminBadgeDeleteView(DeleteView):
    model = Badge
    success_url = reverse_lazy('administration:badge_list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        create_system_log(request, 'BADGE_DELETE', details=f"Badge supprimé : {obj.name}")
        messages.success(request, f"Badge '{obj.name}' supprimé.")
        return super().delete(request, *args, **kwargs)
