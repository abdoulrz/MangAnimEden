"""
Tests for the Friendship model and related User methods (Phase 2.5.2).
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from social.models import Friendship
from django.db import IntegrityError

User = get_user_model()


class FriendshipModelTests(TestCase):
    """Test cases for the Friendship model."""
    
    def setUp(self):
        """Create test users."""
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            nickname='User One',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            nickname='User Two',
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            email='user3@test.com',
            nickname='User Three',
            password='testpass123'
        )
    
    def test_create_friendship_request(self):
        """Test creating a friend request."""
        friendship = Friendship.objects.create(
            requester=self.user1,
            receiver=self.user2,
            status='pending'
        )
        
        self.assertEqual(friendship.requester, self.user1)
        self.assertEqual(friendship.receiver, self.user2)
        self.assertEqual(friendship.status, 'pending')
        self.assertTrue(friendship.is_pending())
        self.assertFalse(friendship.is_accepted())
    
    def test_accept_friendship(self):
        """Test accepting a friend request."""
        friendship = Friendship.objects.create(
            requester=self.user1,
            receiver=self.user2
        )
        
        friendship.accept()
        friendship.refresh_from_db()
        
        self.assertEqual(friendship.status, 'accepted')
        self.assertTrue(friendship.is_accepted())
        self.assertFalse(friendship.is_pending())
    
    def test_unique_constraint(self):
        """Test that duplicate friendships cannot be created."""
        Friendship.objects.create(
            requester=self.user1,
            receiver=self.user2
        )
        
        # Try to create duplicate - should raise IntegrityError
        with self.assertRaises(IntegrityError):
            Friendship.objects.create(
                requester=self.user1,
                receiver=self.user2
            )
    
    def test_friendship_string_representation(self):
        """Test the string representation of a friendship."""
        friendship = Friendship.objects.create(
            requester=self.user1,
            receiver=self.user2,
            status='pending'
        )
        
        expected = f"{self.user1.nickname} -> {self.user2.nickname} (pending)"
        self.assertEqual(str(friendship), expected)


class UserFriendMethodsTests(TestCase):
    """Test cases for User model friend-related methods."""
    
    def setUp(self):
        """Create test users and friendships."""
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            nickname='User One',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            nickname='User Two',
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            email='user3@test.com',
            nickname='User Three',
            password='testpass123'
        )
        self.user4 = User.objects.create_user(
            email='user4@test.com',
            nickname='User Four',
            password='testpass123'
        )
    
    def test_get_friends(self):
        """Test getting list of accepted friends."""
        # Create accepted friendships
        Friendship.objects.create(
            requester=self.user1,
            receiver=self.user2,
            status='accepted'
        )
        Friendship.objects.create(
            requester=self.user3,
            receiver=self.user1,
            status='accepted'
        )
        
        # Create pending friendship (should not appear)
        Friendship.objects.create(
            requester=self.user1,
            receiver=self.user4,
            status='pending'
        )
        
        friends = self.user1.get_friends()
        
        self.assertEqual(friends.count(), 2)
        self.assertIn(self.user2, friends)
        self.assertIn(self.user3, friends)
        self.assertNotIn(self.user4, friends)
    
    def test_get_friend_count(self):
        """Test getting count of friends."""
        # Initially zero
        self.assertEqual(self.user1.get_friend_count(), 0)
        
        # Add friends
        Friendship.objects.create(
            requester=self.user1,
            receiver=self.user2,
            status='accepted'
        )
        Friendship.objects.create(
            requester=self.user3,
            receiver=self.user1,
            status='accepted'
        )
        
        self.assertEqual(self.user1.get_friend_count(), 2)
    
    def test_get_pending_requests(self):
        """Test getting pending friend requests received."""
        Friendship.objects.create(
            requester=self.user2,
            receiver=self.user1,
            status='pending'
        )
        Friendship.objects.create(
            requester=self.user3,
            receiver=self.user1,
            status='pending'
        )
        
        # This one is sent BY user1, not received
        Friendship.objects.create(
            requester=self.user1,
            receiver=self.user4,
            status='pending'
        )
        
        pending = self.user1.get_pending_requests()
        
        self.assertEqual(pending.count(), 2)
        self.assertEqual(pending.filter(requester=self.user2).count(), 1)
        self.assertEqual(pending.filter(requester=self.user3).count(), 1)
    
    def test_get_pending_requests_count(self):
        """Test getting count of pending requests."""
        self.assertEqual(self.user1.get_pending_requests_count(), 0)
        
        Friendship.objects.create(
            requester=self.user2,
            receiver=self.user1,
            status='pending'
        )
        
        self.assertEqual(self.user1.get_pending_requests_count(), 1)
    
    def test_is_friend_with(self):
        """Test checking if two users are friends."""
        # Not friends initially
        self.assertFalse(self.user1.is_friend_with(self.user2))
        
        # Create pending friendship - should still be False
        Friendship.objects.create(
            requester=self.user1,
            receiver=self.user2,
            status='pending'
        )
        self.assertFalse(self.user1.is_friend_with(self.user2))
        
        # Accept friendship - now should be True
        friendship = Friendship.objects.get(requester=self.user1, receiver=self.user2)
        friendship.accept()
        
        self.assertTrue(self.user1.is_friend_with(self.user2))
        self.assertTrue(self.user2.is_friend_with(self.user1))  # Bidirectional
    
    def test_has_pending_request_from(self):
        """Test checking if user has pending request from another user."""
        self.assertFalse(self.user1.has_pending_request_from(self.user2))
        
        Friendship.objects.create(
            requester=self.user2,
            receiver=self.user1,
            status='pending'
        )
        
        self.assertTrue(self.user1.has_pending_request_from(self.user2))
        self.assertFalse(self.user2.has_pending_request_from(self.user1))
    
    def test_has_sent_request_to(self):
        """Test checking if user has sent request to another user."""
        self.assertFalse(self.user1.has_sent_request_to(self.user2))
        
        Friendship.objects.create(
            requester=self.user1,
            receiver=self.user2,
            status='pending'
        )
        
        self.assertTrue(self.user1.has_sent_request_to(self.user2))
        self.assertFalse(self.user2.has_sent_request_to(self.user1))
    
    def test_bidirectional_friendship(self):
        """Test that friendships work in both directions."""
        # user1 requests user2
        Friendship.objects.create(
            requester=self.user1,
            receiver=self.user2,
            status='accepted'
        )
        
        # Both should see each other as friends
        self.assertTrue(self.user1.is_friend_with(self.user2))
        self.assertTrue(self.user2.is_friend_with(self.user1))
        
        # Both should have friend_count = 1
        self.assertEqual(self.user1.get_friend_count(), 1)
        self.assertEqual(self.user2.get_friend_count(), 1)
        
        # Both should have each other in friends list
        self.assertIn(self.user2, self.user1.get_friends())
        self.assertIn(self.user1, self.user2.get_friends())
    
    def test_no_duplicate_friends(self):
        """Test that get_friends() doesn't return duplicates."""
        # Create friendship
        Friendship.objects.create(
            requester=self.user1,
            receiver=self.user2,
            status='accepted'
        )
        
        friends = self.user1.get_friends()
        
        # Ensure no duplicates
        self.assertEqual(friends.count(), friends.distinct().count())
        self.assertEqual(friends.filter(id=self.user2.id).count(), 1)
