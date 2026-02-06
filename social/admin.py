from django.contrib import admin
from .models import Group, Event, Message, Friendship

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location')
    list_filter = ('date',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'group', 'timestamp')
    list_filter = ('group', 'timestamp')

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('requester', 'receiver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('requester__nickname', 'receiver__nickname')
    readonly_fields = ('created_at', 'updated_at')

