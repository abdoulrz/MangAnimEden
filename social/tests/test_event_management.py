from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from social.models import Event
from django.utils import timezone

User = get_user_model()

class EventManagementTests(TestCase):
    def setUp(self):
        # Users
        self.user_low = User.objects.create_user(email='low@example.com', password='password', nickname='LowLvl', level=10)
        self.user_high = User.objects.create_user(email='high@example.com', password='password', nickname='Yonko', level=65)
        self.staff = User.objects.create_user(email='staff@example.com', password='password', nickname='Staff', is_staff=True)
        
        # Event
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Desc",
            date=timezone.now() + timezone.timedelta(days=1),
            location="Test Location",
            organizer=self.user_high
        )
        
        self.client = Client()

    def test_user_levels_correctly_set(self):
        """Debug test to ensure level is correctly saved via create_user."""
        self.assertEqual(self.user_low.level, 10)
        self.assertEqual(self.user_high.level, 65)

    def test_event_creation_restricted_to_lvl_65(self):
        """Test that only Level 65+ users can create events."""
        self.client.force_login(self.user_low)
        # Low level try - should fail
        self.client.post(reverse('social:forum_home'), {
            'event_title': '1', # Trigger
            'title': 'New Event Fail',
            'description': 'New Desc',
            'date': '2026-12-31 12:00', # Format check
            'location': 'Somewhere'
        })
        self.assertFalse(Event.objects.filter(title='New Event Fail').exists())
        
        self.client.force_login(self.user_high)
        # High level try - should succeed
        self.client.post(reverse('social:forum_home'), {
            'event_title': '1', # Trigger
            'title': 'New Event Success',
            'description': 'New Desc',
            'date': '2026-12-31 12:00',
            'location': 'Somewhere'
        })
        self.assertTrue(Event.objects.filter(title='New Event Success').exists())

    def test_event_deletion_restricted_to_lvl_65(self):
        """Test that only Level 65+ users can delete events."""
        self.client.force_login(self.user_low)
        self.client.get(reverse('social:delete_event', args=[self.event.id]), follow=True)
        self.assertTrue(Event.objects.filter(id=self.event.id).exists())
        
        self.client.force_login(self.user_high)
        # Use a fresh event for high level test because we don't want to conflict with other tests
        event_to_del = Event.objects.create(
            title="Del Me",
            date=timezone.now() + timezone.timedelta(days=1),
            organizer=self.user_low
        )
        self.client.get(reverse('social:delete_event', args=[event_to_del.id]), follow=True)
        self.assertFalse(Event.objects.filter(id=event_to_del.id).exists())

    def test_staff_can_delete_any_event(self):
        """Test that staff can delete events regardless of level."""
        self.client.force_login(self.staff)
        self.client.get(reverse('social:delete_event', args=[self.event.id]), follow=True)
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())
