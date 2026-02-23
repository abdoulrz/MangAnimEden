from django.urls import path
from . import views

app_name = 'reader'

urlpatterns = [
    path('chap/', views.chap_view, name='chap'),
    path('chap/<int:chapter_id>/', views.chap_view, name='chap_chapter'),
]
