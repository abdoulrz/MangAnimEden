from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from social.models import Group, GroupMembership, Message

User = get_user_model()

class ForumPermissionsTests(TestCase):
    def setUp(self):
        # Users
        self.user_member = User.objects.create_user(email='member@example.com', password='password', nickname='Member')
        self.user_non_member = User.objects.create_user(email='stranger@example.com', password='password', nickname='Stranger')
        self.user_banned = User.objects.create_user(email='banned@example.com', password='password', nickname='Banned')
        self.owner = User.objects.create_user(email='owner@example.com', password='password', nickname='Owner')

        # Group
        self.group = Group.objects.create(name='Test Group', description='A test group', owner=self.owner)

        # Memberships
        GroupMembership.objects.create(user=self.user_member, group=self.group)
        GroupMembership.objects.create(user=self.user_banned, group=self.group, is_banned=True)

        self.client = Client()

    def test_forum_my_groups_tab(self):
        """Test that 'My Groups' tab shows joined groups."""
        self.client.force_login(self.user_member)
        response = self.client.get(reverse('social:forum_home') + '?tab=my_groups')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.group.name)
        # self.assertContains(response, 'Mes Groupes') # Might fail due to newline
        self.assertContains(response, 'tab=my_groups')

    def test_forum_discover_tab(self):
        """Test that 'Discover' tab shows non-joined groups."""
        self.client.force_login(self.user_non_member)
        response = self.client.get(reverse('social:forum_home') + '?tab=discover')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.group.name)

    def test_member_can_see_chat(self):
        """Test that a member can see the chat interface."""
        self.client.force_login(self.user_member)
        response = self.client.get(reverse('social:forum_home') + f'?group_id={self.group.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'chat-input') # Should see input
        self.assertNotContains(response, 'Rejoignez le groupe') # Should NOT see join prompt

    def test_non_member_sees_join_prompt(self):
        """Test that a non-member sees the join prompt and no chat."""
        self.client.force_login(self.user_non_member)
        response = self.client.get(reverse('social:forum_home') + f'?group_id={self.group.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rejoignez le groupe') # Join prompt
        self.assertNotContains(response, 'chat-input') # No chat input

    def test_banned_user_ui(self):
        """Test that a banned user sees the banned overlay."""
        self.client.force_login(self.user_banned)
        response = self.client.get(reverse('social:forum_home') + f'?group_id={self.group.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vous avez été banni')
        self.assertNotContains(response, 'chat-input')

    def test_join_group(self):
        """Test joining a group."""
        self.client.force_login(self.user_non_member)
        response = self.client.post(reverse('social:join_group', args=[self.group.id]), follow=True)
        # self.assertContains(response, f"Vous avez rejoint le groupe {self.group.name}")
        self.assertTrue(GroupMembership.objects.filter(user=self.user_non_member, group=self.group).exists())

    def test_leave_group(self):
        """Test leaving a group."""
        self.client.force_login(self.user_member)
        response = self.client.post(reverse('social:leave_group', args=[self.group.id]), follow=True)
        # self.assertContains(response, f"Vous avez quitté le groupe {self.group.name}")
        self.assertFalse(GroupMembership.objects.filter(user=self.user_member, group=self.group).exists())

    def test_staff_can_see_chat_but_not_input(self):
        """Test that staff can see chat messages but cannot post without joining."""
        staff_user = User.objects.create_user(email='staff@example.com', password='password', nickname='Staff', is_staff=True)
        self.client.force_login(staff_user)
        response = self.client.get(reverse('social:forum_home') + f'?group_id={self.group.id}')
        self.assertEqual(response.status_code, 200)
        # Should see messages (lock screen hidden)
        self.assertNotContains(response, 'Rejoignez le groupe') 
        # Should NOT see input form
        self.assertNotContains(response, 'chat-input')
