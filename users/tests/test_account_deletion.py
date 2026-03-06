from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from social.models import Group, Message

User = get_user_model()

class AccountDeletionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('users:account_delete')
        
        # Create a user
        self.user = User.objects.create_user(
            email='delete_me@example.com',
            nickname='DeleteMe',
            password='StrongPassword123!'
        )
        
        # Create a social group and a message sent by the user
        self.group = Group.objects.create(name='Test Group', description='Group for testing')
        self.message = Message.objects.create(
            group=self.group,
            sender=self.user,
            content='This message should survive user deletion'
        )

    def test_account_deletion_view_get(self):
        """Ensure the warning page is rendered on GET"""
        self.client.login(email='delete_me@example.com', password='StrongPassword123!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/account_delete_confirm.html')

    def test_account_deletion_without_confirmation(self):
        """Ensure deletion does not happen if checkbox is not checked"""
        self.client.login(email='delete_me@example.com', password='StrongPassword123!')
        # Submitting without 'confirm_delete': 'yes'
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200) # Re-renders form with error
        
        # User should still exist
        self.assertTrue(User.objects.filter(email='delete_me@example.com').exists())

    def test_account_deletion_with_confirmation_preserves_messages(self):
        """Ensure deletion works, logs user out, and sets message sender to NULL"""
        self.client.login(email='delete_me@example.com', password='StrongPassword123!')
        response = self.client.post(self.url, {'confirm_delete': 'yes'})
        
        # Expect redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        
        # User should be deleted
        self.assertFalse(User.objects.filter(email='delete_me@example.com').exists())
        
        # Logged out (session should be cleared)
        self.assertNotIn('_auth_user_id', self.client.session)
        
        # GDPR Check: Message should survive, but sender should be NULL
        self.message.refresh_from_db()
        self.assertIsNone(self.message.sender)
        self.assertEqual(self.message.content, 'This message should survive user deletion')
