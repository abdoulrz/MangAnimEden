from django.urls import path
from . import views

urlpatterns = [
    path('', views.forum_home, name='forum_home'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
]
