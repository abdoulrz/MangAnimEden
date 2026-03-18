from django.contrib import admin
from django.utils.html import format_html
from .models import Group, Event, Message, Friendship

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('get_tag', 'name', 'owner', 'created_at')
    search_fields = ('name', 'owner__nickname')
    list_filter = ('created_at',)
    
    def get_tag(self, obj):
        return format_html('<span style="background: #6c5ce7; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 10px;">GROUP</span>')
    get_tag.short_description = 'Type'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('get_tag', 'title', 'date', 'location', 'organizer')
    list_filter = ('date',)
    search_fields = ('title', 'location', 'organizer__nickname')
    
    def get_tag(self, obj):
        return format_html('<span style="background: #e67e22; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 10px;">EVENT</span>')
    get_tag.short_description = 'Type'

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

