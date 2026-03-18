from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from users.models import User
from social.models import Group, Message, Event, DirectMessage, GroupMembership
from datetime import timedelta

class SidebarUnificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com', 
            password='password123', 
            nickname='Tester',
            level=65  # Yonko Commander
        )
        self.client.login(email='test@example.com', password='password123')
        
        # Create a group
        self.group = Group.objects.create(name="Test Group", owner=self.user)
        GroupMembership.objects.create(group=self.group, user=self.user)
        
        # Create a DM partner
        self.other_user = User.objects.create_user(email='other@example.com', password='password123', nickname='Other')
        DirectMessage.objects.create(sender=self.user, recipient=self.other_user, content="Hello")
        
        # Create an event
        self.event = Event.objects.create(
            title="Test Event",
            description="Details",
            date=timezone.now() + timedelta(days=1),
            organizer=self.user
        )

    def test_sidebar_includes_all_types(self):
        """Verify that Groups, DMs, and Events are in sidebar_items."""
        response = self.client.get(reverse('social:forum_home'))
        self.assertEqual(response.status_code, 200)
        
        sidebar_items = response.context['sidebar_items']
        types = [item['type'] for item in sidebar_items]
        
        self.assertIn('group', types)
        self.assertIn('dm', types)
        self.assertIn('event', types)
        
    def test_sidebar_sorting_lifo(self):
        """Verify items are sorted by activity/date."""
        # Event is in the future, should be at the top if sorting by last_activity DESC
        response = self.client.get(reverse('social:forum_home'))
        sidebar_items = response.context['sidebar_items']
        
        # First item should be the event because its 'date' is in the future
        self.assertEqual(sidebar_items[0]['type'], 'event')
        self.assertEqual(sidebar_items[0]['name'], "Test Event")

    def test_event_badge_presence_in_html(self):
        """Check if curated tags are rendered in HTML."""
        response = self.client.get(reverse('social:forum_home'))
        content = response.content.decode()
        
        self.assertIn('tag-group', content)
        self.assertIn('tag-dm', content)
        self.assertIn('tag-event', content)
        self.assertIn('GROUP', content)
        self.assertIn('DM', content)
        self.assertIn('EVENT', content)
