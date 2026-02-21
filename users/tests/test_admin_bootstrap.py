"""
Tests for the admin bootstrap passphrase feature on registration.

Covers:
1. Correct passphrase → user gets is_superuser + is_staff + role_admin
2. Wrong passphrase → user is a normal Reader
3. Blank passphrase → user is a normal Reader
4. Passphrase works up to MAX (5) admins; 6th attempt is silently demoted
5. Deleting an admin frees the spot (count-based, so naturally automatic)
"""
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

PASSPHRASE = 'Nefe'

@override_settings(
    ADMIN_BOOTSTRAP_PASSPHRASE=PASSPHRASE,
    ADMIN_BOOTSTRAP_MAX=5,
)
class AdminBootstrapTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('register')

    def _register(self, nickname, email, passphrase=''):
        self.client.logout()  # Ensure we aren't logged in from a previous iteration
        return self.client.post(self.url, {
            'nickname': nickname,
            'email': email,
            'password1': 'StrongPass2026!',
            'password2': 'StrongPass2026!',
            'admin_passphrase': passphrase,
        })

    # ------------------------------------------------------------------
    # 1. Correct passphrase → promoted to admin
    # ------------------------------------------------------------------
    def test_correct_passphrase_creates_admin(self):
        response = self._register('Founder1', 'founder1@test.com', PASSPHRASE)
        self.assertRedirects(response, reverse('home'))
        user = User.objects.get(email='founder1@test.com')
        self.assertTrue(user.is_superuser, "is_superuser should be True")
        self.assertTrue(user.is_staff, "is_staff should be True")
        self.assertTrue(user.role_admin, "role_admin should be True")

    # ------------------------------------------------------------------
    # 2. Wrong passphrase → stays Reader
    # ------------------------------------------------------------------
    def test_wrong_passphrase_creates_reader(self):
        response = self._register('NormalUser', 'normal@test.com', 'WrongCode')
        self.assertRedirects(response, reverse('home'))
        user = User.objects.get(email='normal@test.com')
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.role_admin)

    # ------------------------------------------------------------------
    # 3. Blank passphrase → stays Reader
    # ------------------------------------------------------------------
    def test_blank_passphrase_creates_reader(self):
        response = self._register('Reader1', 'reader1@test.com', '')
        self.assertRedirects(response, reverse('home'))
        user = User.objects.get(email='reader1@test.com')
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.role_admin)

    # ------------------------------------------------------------------
    # 4. Max 5 admins — the 6th is silently a Reader
    # ------------------------------------------------------------------
    def test_passphrase_respects_max_limit(self):
        for i in range(1, 6):  # Create 5 admins
            self._register(f'Admin{i}', f'admin{i}@test.com', PASSPHRASE)

        self.assertEqual(User.objects.filter(role_admin=True).count(), 5)

        # 6th attempt — should be a Reader
        self._register('Admin6', 'admin6@test.com', PASSPHRASE)
        user6 = User.objects.get(email='admin6@test.com')
        self.assertFalse(user6.role_admin, "6th admin should NOT be promoted")
        self.assertFalse(user6.is_superuser)

    # ------------------------------------------------------------------
    # 5. Deleting an admin frees the spot
    # ------------------------------------------------------------------
    def test_deleting_admin_frees_spot(self):
        # Fill up to exactly 5 admins
        for i in range(1, 6):
            self._register(f'Admin{i}', f'admin{i}@test.com', PASSPHRASE)

        self.assertEqual(User.objects.filter(role_admin=True).count(), 5)

        # Delete one admin
        User.objects.get(email='admin1@test.com').delete()
        self.assertEqual(User.objects.filter(role_admin=True).count(), 4)

        # Now a new registration with the passphrase should succeed
        self._register('NewAdmin', 'newadmin@test.com', PASSPHRASE)
        new_user = User.objects.get(email='newadmin@test.com')
        self.assertTrue(new_user.role_admin, "Spot freed — new admin should be promoted")
        self.assertTrue(new_user.is_superuser)
