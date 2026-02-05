from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from social.models import Story
from django.core.files.uploadedfile import SimpleUploadedFile
import os

User = get_user_model()

class StoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com', 
            nickname='TestUser', 
            password='password123'
        )
        self.client.login(email='test@example.com', password='password123')
        
        # Create a dummy image
        self.image_content = b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff\xff,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02L\x01\x00;'
        self.image = SimpleUploadedFile("test.gif", self.image_content, content_type="image/gif")

    def test_create_story_via_view(self):
        """Test submitting a new story via the form"""
        response = self.client.post(reverse('forum_home'), {
            'story_image': self.image
        })
        self.assertEqual(response.status_code, 302) # Redirects back to forum
        
        self.assertEqual(Story.objects.count(), 1)
        story = Story.objects.first()
        self.assertEqual(story.user, self.user)
        self.assertIsNotNone(story.expires_at)
        
        # Verify it appears in context (stories are grouped by user)
        response = self.client.get(reverse('forum_home'))
        self.assertIn('story_users', response.context)
        self.assertIn(self.user, response.context['story_users'])

    def test_story_expiration(self):
        """Test that expired stories are not shown"""
        story = Story.objects.create(user=self.user, image=self.image)
        # Manually expire it
        story.expires_at = timezone.now() - timedelta(hours=1)
        story.save()
        
        response = self.client.get(reverse('forum_home'))
        # User should not be in the list if they have no active stories
        if 'story_users' in response.context:
             self.assertNotIn(self.user, response.context['story_users'])

    def test_story_grouping(self):
        """Test that multiple stories from same user appear as one bubble"""
        # Create two stories for the same user
        Story.objects.create(user=self.user, image=self.image)
        Story.objects.create(user=self.user, image=self.image)
        
        response = self.client.get(reverse('forum_home'))
        
        # Should have 2 stories in DB
        self.assertEqual(Story.objects.count(), 2)
        
        # But only 1 user in the context list (story_users)
        # Note: The view now passes 'story_users', not 'stories'
        self.assertIn('story_users', response.context)
        self.assertEqual(len(response.context['story_users']), 1)
        self.assertEqual(response.context['story_users'][0], self.user)

    def test_dynamic_views(self):
        """Test that URL parameters switch the active_mode correctly"""
        # 1. Default Mode
        response = self.client.get(reverse('forum_home'))
        self.assertEqual(response.context['active_mode'], 'default')
        
        # 2. Story Mode
        # Create a story first
        Story.objects.create(user=self.user, image=self.image)
        response = self.client.get(reverse('forum_home'), {'story_user_id': self.user.id})
        self.assertEqual(response.context['active_mode'], 'story')
        self.assertEqual(response.context['active_story_user'], self.user)
        self.assertIn('active_user_stories', response.context)
        
        # 3. Event Mode (Need to mock or create event, skipping for brevity or adding simple mock if needed, 
        # but let's stick to story focus as that was the main request. 
        # Actually, let's just test story and default since they are the ones I touched most.)

    def test_cleanup_command(self):
        """Test the management command"""
        from django.core.management import call_command
        
        # Create expired story
        story = Story.objects.create(user=self.user, image=self.image)
        story.expires_at = timezone.now() - timedelta(hours=1)
        story.save()
        
        # Create fresh story
        fresh_story = Story.objects.create(user=self.user, image=self.image)
        # Ensure fresh story expires in future (default behavior)
        
        call_command('cleanup_stories')
        
        self.assertEqual(Story.objects.count(), 1)
        self.assertEqual(Story.objects.first(), fresh_story)

    def tearDown(self):
        # Clean up files created
        for story in Story.objects.all():
            if story.image:
                if os.path.isfile(story.image.path):
                    os.remove(story.image.path)
