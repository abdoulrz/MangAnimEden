from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from social.models import Group, GroupMembership

User = get_user_model()

class GroupManagementTests(TestCase):
    def setUp(self):
        # Create Users
        self.admin_user = User.objects.create_user(email='admin@test.com', password='password', nickname='AdminUser', is_staff=True, level=100)
        self.high_level_user = User.objects.create_user(email='high@test.com', password='password', nickname='HighLevelUser', level=50) # Level 50 = Can create 1 group
        self.low_level_user = User.objects.create_user(email='low@test.com', password='password', nickname='LowLevelUser', level=10) # Level 10 = Cannot create group
        self.member_user = User.objects.create_user(email='member@test.com', password='password', nickname='MemberUser', level=20)
        
        self.client = Client()

    def test_group_creation_permission(self):
        """Test that only Level 50+ users can create groups."""
        
        # 1. Low Level User try
        self.client.login(email='low@test.com', password='password')
        response = self.client.get(reverse('social:create_group'))
        # Expect redirect or error message (implementation redirects to forum_home)
        self.assertRedirects(response, reverse('social:forum_home')) 
        
        # 2. High Level User try
        self.client.login(email='high@test.com', password='password')
        response = self.client.get(reverse('social:create_group'))
        self.assertEqual(response.status_code, 200) # Should see form

    def test_group_creation_quota(self):
        """Test that group creation is limited by level."""
        self.client.login(email='high@test.com', password='password')
        
        # Create 1st group (Allowed for Level 50)
        response = self.client.post(reverse('social:create_group'), {
            'name': 'Group 1',
            'description': 'Test Description'
        })
        self.assertRedirects(response, reverse('social:forum_home'))
        self.assertEqual(Group.objects.count(), 1)
        
        # Create 2nd group (Should fail, max=1)
        response = self.client.post(reverse('social:create_group'), {
            'name': 'Group 2',
            'description': 'Test Description 2'
        })
        # Expect redirect back to forum due to error (or stay on page with error)
        # Our implementation redirects to forum_home with error message
        self.assertRedirects(response, reverse('social:forum_home'))
        self.assertEqual(Group.objects.count(), 1)

    def test_ban_user(self):
        """Test that group owner can ban a user."""
        # Create group owned by HighLevelUser
        group = Group.objects.create(name='Test Group', owner=self.high_level_user)
        # Create membership
        GroupMembership.objects.create(group=group, user=self.member_user)
        
        # High level user logs in
        self.client.login(email='high@test.com', password='password')
        
        # Ban MemberUser
        url = reverse('social:ban_user', args=[group.id, self.member_user.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(GroupMembership.objects.get(group=group, user=self.member_user).is_banned)
        
        # Unban MemberUser
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(GroupMembership.objects.get(group=group, user=self.member_user).is_banned)

    def test_ban_user_permission_denied(self):
        """Test that non-owner cannot ban users."""
        group = Group.objects.create(name='Test Group', owner=self.high_level_user)
        GroupMembership.objects.create(group=group, user=self.member_user)
        
        # Low level user logs in
        self.client.login(email='low@test.com', password='password')
        
        # Try to Ban MemberUser
        url = reverse('social:ban_user', args=[group.id, self.member_user.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403) # Forbidden
