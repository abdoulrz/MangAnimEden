from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    path('', views.forum_home, name='forum_home'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
    
    # Friendship URLs (Phase 2.5.2)
    path('friends/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friends/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friends/reject/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('friends/remove/<int:user_id>/', views.remove_friend, name='remove_friend'),
    path('friends/list/', views.friend_list, name='friend_list'),
    path('friends/list/<int:user_id>/', views.friend_list, name='friend_list_user'),
    
    # Social Discovery (Phase 2.5.2.1)
    path('users/search/', views.user_search_view, name='user_search'),
    
    # Group Management (Phase 2.5.4 & 2.5.5)
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/<int:group_id>/ban/<int:user_id>/', views.ban_user, name='ban_user'),
]

