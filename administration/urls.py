from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    # Dashboard
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    
    # User Management
    path('users/', views.UserManagementView.as_view(), name='user_list'),
    path('users/action/', views.UserActionView.as_view(), name='user_action'),
    
    # Content Management - Series
    path('content/series/', views.AdminSeriesListView.as_view(), name='series_list'),
    path('content/series/create/', views.AdminSeriesCreateView.as_view(), name='series_create'),
    path('content/series/<int:pk>/edit/', views.AdminSeriesUpdateView.as_view(), name='series_edit'),
    path('content/series/<int:pk>/delete/', views.AdminSeriesDeleteView.as_view(), name='series_delete'),
    
    # Content Management - Chapters
    path('content/series/<int:series_id>/chapters/', views.AdminChapterListView.as_view(), name='chapter_list'),
    path('content/series/<int:series_id>/chapters/create/', views.AdminChapterCreateView.as_view(), name='chapter_create'),
    path('content/chapters/<int:pk>/edit/', views.AdminChapterUpdateView.as_view(), name='chapter_edit'),
    path('content/chapters/<int:pk>/delete/', views.AdminChapterDeleteView.as_view(), name='chapter_delete'),
    
    # Content Management - Genres
    path('content/genres/', views.AdminGenreListView.as_view(), name='genre_list'),
    path('content/genres/create/', views.AdminGenreCreateView.as_view(), name='genre_create'),
    path('content/genres/<int:pk>/edit/', views.AdminGenreUpdateView.as_view(), name='genre_edit'),
    path('content/genres/<int:pk>/delete/', views.AdminGenreDeleteView.as_view(), name='genre_delete'),

    # Community Management - Groups
    path('community/groups/', views.AdminGroupListView.as_view(), name='group_list'),
    path('community/groups/<int:pk>/edit/', views.AdminGroupUpdateView.as_view(), name='group_edit'),
    path('community/groups/<int:pk>/delete/', views.AdminGroupDeleteView.as_view(), name='group_delete'),
]
