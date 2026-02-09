from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from administration.models import SystemLog
from catalog.models import Series, Genre
from social.models import Group

User = get_user_model()

class AdminAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(nickname='super', email='super@test.com', password='password')
        self.admin = User.objects.create_user(nickname='admin', email='admin@test.com', password='password', role_admin=True)
        self.mod = User.objects.create_user(nickname='mod', email='mod@test.com', password='password', role_moderator=True)
        self.user = User.objects.create_user(nickname='user', email='user@test.com', password='password')

    def test_dashboard_access(self):
        # Superuser and Admin should access
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('administration:dashboard'))
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.admin)
        response = self.client.get(reverse('administration:dashboard'))
        self.assertEqual(response.status_code, 200)

        # Mod and User should get 404 (as per requires_admin)
        self.client.force_login(self.mod)
        response = self.client.get(reverse('administration:dashboard'))
        self.assertEqual(response.status_code, 404)

        self.client.force_login(self.user)
        response = self.client.get(reverse('administration:dashboard'))
        self.assertEqual(response.status_code, 404)

    def test_user_list_access(self):
        # Mod should access (UserManagementView is requires_moderator)
        self.client.force_login(self.mod)
        response = self.client.get(reverse('administration:user_list'))
        self.assertEqual(response.status_code, 200)

        # User should get 404
        self.client.force_login(self.user)
        response = self.client.get(reverse('administration:user_list'))
        self.assertEqual(response.status_code, 404)

    def test_series_list_access(self):
        # Admin only (requires_admin)
        self.client.force_login(self.admin)
        response = self.client.get(reverse('administration:series_list'))
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.mod)
        response = self.client.get(reverse('administration:series_list'))
        self.assertEqual(response.status_code, 404)

    def test_group_list_access(self):
        # Mod allowed (requires_moderator)
        self.client.force_login(self.mod)
        response = self.client.get(reverse('administration:group_list'))
        self.assertEqual(response.status_code, 200)

class AdminActionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(nickname='admin', email='admin@test.com', password='password', role_admin=True)
        self.target_user = User.objects.create_user(nickname='target', email='target@test.com', password='password')

    def test_ban_user_action(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('administration:user_action'), {
            'user_id': self.target_user.id,
            'action': 'toggle_ban'
        }, follow=True)
        
        self.target_user.refresh_from_db()
        self.assertTrue(self.target_user.is_banned)
        self.assertFalse(self.target_user.is_active)
        
        # Check log
        log = SystemLog.objects.first()
        self.assertIsNotNone(log)
        self.assertEqual(log.actor, self.admin)
        self.assertEqual(log.target_user, self.target_user)
        # Action stored might be 'USER_ACTION' from decorator or we'd need to check message
        self.assertEqual(log.action, 'USER_ACTION') 

    def test_promote_mod_action(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('administration:user_action'), {
            'user_id': self.target_user.id,
            'action': 'toggle_moderator'
        }, follow=True)
        
        self.target_user.refresh_from_db()
        self.assertTrue(self.target_user.role_moderator)

class ContentManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(nickname='admin', email='admin@test.com', password='password', role_admin=True)
        self.genre = Genre.objects.create(name='Action', slug='action')
        
    def test_create_series(self):
        self.client.force_login(self.admin)
        data = {
            'title': 'New Series',
            'slug': 'new-series',
            'description': 'Description',
            'type': 'manga',
            'status': 'ongoing',
            'genres': [self.genre.id]
        }
        response = self.client.post(reverse('administration:series_create'), data)
        self.assertEqual(Series.objects.count(), 1)
        self.assertEqual(Series.objects.first().title, 'New Series')
        
        # Check log
        self.assertTrue(SystemLog.objects.filter(action='SERIES_CREATE').exists())
