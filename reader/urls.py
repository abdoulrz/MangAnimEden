from django.urls import path
from . import views

app_name = 'reader'

urlpatterns = [
    path('demo/', views.demo_view, name='demo'),
]
