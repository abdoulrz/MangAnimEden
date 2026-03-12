from django.urls import path
from . import views, api_views

app_name = 'reader'

urlpatterns = [
    path('chap/', views.chap_view, name='chap'),
    path('chap/<int:chapter_id>/', views.chap_view, name='chap_chapter'),
    path('api/progress/', api_views.update_progress, name='update_progress'),
]
