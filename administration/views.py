from django.shortcuts import get_object_or_404, redirect
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

User = get_user_model()

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
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset

from catalog.services import bulk_create_chapters_from_folder
from .forms import SeriesForm

@method_decorator(requires_admin, name='dispatch')
class AdminSeriesCreateView(CreateView):
    model = Series
    form_class = SeriesForm
    template_name = 'administration/content/series_form.html'
    success_url = reverse_lazy('administration:series_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle folder upload
        files = self.request.FILES.getlist('folder_upload')
        
        if files:
            count = bulk_create_chapters_from_folder(self.object, files)
            if count > 0:
                messages.success(self.request, f"{count} chapitres importés.")
            else:
                messages.warning(self.request, "Aucun chapitre n'a pu être traité du dossier.")
                
        create_system_log(self.request, 'SERIES_CREATE', details=f"Série créée : {self.object.title}")
        messages.success(self.request, "Série créée avec succès.")
        return response

@method_decorator(requires_admin, name='dispatch')
class AdminSeriesUpdateView(UpdateView):
    model = Series
    form_class = SeriesForm
    template_name = 'administration/content/series_form.html'
    success_url = reverse_lazy('administration:series_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle folder upload
        files = self.request.FILES.getlist('folder_upload')
        if files:
            count = bulk_create_chapters_from_folder(self.object, files)
            if count > 0:
                messages.success(self.request, f"{count} chapitres importés.")
            else:
                messages.warning(self.request, "Aucun chapitre n'a pu être traité du dossier.")

        create_system_log(self.request, 'SERIES_UPDATE', details=f"Série modifiée : {self.object.title}")
        messages.success(self.request, "Série mise à jour avec succès.")
        return response

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
        response = super().form_valid(form)
        create_system_log(self.request, 'CHAPTER_CREATE', details=f"Chapitre créé : {self.object.number} pour {self.object.series.title}")
        messages.success(self.request, "Chapitre créé avec succès.")
        return response

@method_decorator(requires_admin, name='dispatch')
class AdminChapterUpdateView(UpdateView):
    model = Chapter
    form_class = ChapterForm
    template_name = 'administration/content/chapter_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # For update, we get the series from the object
        context['current_series'] = self.object.series
        return context

    def get_success_url(self):
        return reverse_lazy('administration:chapter_list', kwargs={'series_id': self.object.series.id})

    def form_valid(self, form):
        response = super().form_valid(form)
        create_system_log(self.request, 'CHAPTER_UPDATE', details=f"Chapitre modifié : {self.object.number} pour {self.object.series.title}")
        messages.success(self.request, "Chapitre mis à jour.")
        return response

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

@method_decorator(requires_moderator, name='dispatch')
class AdminGroupUpdateView(UpdateView):
    model = Group
    template_name = 'administration/community/group_form.html'
    fields = ['name', 'description', 'icon'] # Add status field if available, for now just basic edit
    success_url = reverse_lazy('administration:group_list')
    
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
