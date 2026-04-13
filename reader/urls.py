from django.urls import path
from . import views, api_views

app_name = 'reader'

urlpatterns = [
    # Legacy ID-based redirect (backward compat for bookmarks/links)
    path('chap/<int:chapter_id>/', views.chap_legacy_redirect, name='chap_legacy'),
    path('chap/', views.chap_view, name='chap'),

    # API
    path('api/progress/', api_views.update_progress, name='update_progress'),
    
    # Static paths (Phase 5/6)
    # path('premium/', views.premium_page, name='premium_info'),

    # Clean slug-based URLs (primary catch-all)
    path('<slug:series_slug>/<str:chapter_number>/', views.chap_view, name='chap_chapter'),
    path('unlock/<slug:series_slug>/<str:chapter_number>/', views.unlock_chapter, name='unlock_chapter'),
]
