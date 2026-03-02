from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from social.models import Story, Group
from django.core.files.uploadedfile import SimpleUploadedFile
import os
import shutil
import tempfile

User = get_user_model()

# Use a temporary directory for media during tests
TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage',
    MEDIA_ROOT=TEST_MEDIA_ROOT,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
)
class StoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com', 
            nickname='TestUser', 
            password='password123'
        )
        self.client.login(email='test@example.com', password='password123')
        
        # Create a test group
        self.group = Group.objects.create(name="Test Group", owner=self.user)
        
        # Create a dummy image
        self.image_content = b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff\xff,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02L\x01\x00;'

    def _make_image(self):
        """Helper to create a fresh SimpleUploadedFile for each test."""
        return SimpleUploadedFile("test.gif", self.image_content, content_type="image/gif")

    def test_create_media_story_via_view(self):
        """Test submitting a new image story via the form"""
        self.user.role_moderator = True
        self.user.save()
        
        response = self.client.post(reverse('social:forum_home'), {
            'story_image': self._make_image(),
            'target_group_id': self.group.id
        })
        self.assertEqual(response.status_code, 302)
        
        self.assertEqual(Story.objects.count(), 1)
        story = Story.objects.first()
        self.assertEqual(story.user, self.user)
        self.assertEqual(story.group, self.group)
        self.assertEqual(story.node_type, 'media')
        self.assertIsNotNone(story.expires_at)
        
        response = self.client.get(reverse('social:forum_home'))
        self.assertIn('story_groups', response.context)
        self.assertIn(self.group, response.context['story_groups'])

    def test_create_text_story_via_view(self):
        """Test submitting a new text story via the form"""
        self.user.role_moderator = True
        self.user.save()
        
        response = self.client.post(reverse('social:forum_home'), {
            'story_text': 'Hello World!',
            'story_bg_color': '#e74c3c',
            'target_group_id': self.group.id
        })
        self.assertEqual(response.status_code, 302)
        
        self.assertEqual(Story.objects.count(), 1)
        story = Story.objects.first()
        self.assertEqual(story.node_type, 'text')
        self.assertEqual(story.text_content, 'Hello World!')
        self.assertEqual(story.background_color, '#e74c3c')
        self.assertFalse(story.image)  # No image for text stories

    def test_story_expiration(self):
        """Test that expired stories are not shown"""
        story = Story.objects.create(user=self.user, image=self._make_image(), group=self.group)
        story.expires_at = timezone.now() - timedelta(hours=1)
        story.save()
        
        response = self.client.get(reverse('social:forum_home'))
        if 'story_groups' in response.context:
             self.assertNotIn(self.group, response.context['story_groups'])

    def test_story_grouping(self):
        """Test that multiple stories from same group appear as one bubble"""
        Story.objects.create(user=self.user, image=self._make_image(), group=self.group)
        Story.objects.create(user=self.user, image=self._make_image(), group=self.group)
        
        response = self.client.get(reverse('social:forum_home'))
        
        self.assertEqual(Story.objects.count(), 2)
        self.assertIn('story_groups', response.context)
        self.assertEqual(len(response.context['story_groups']), 1)
        self.assertEqual(response.context['story_groups'][0], self.group)

    def test_dynamic_views(self):
        """Test that URL parameters switch the active_mode correctly"""
        response = self.client.get(reverse('social:forum_home'))
        self.assertEqual(response.context['active_mode'], 'default')
        
        Story.objects.create(user=self.user, image=self._make_image(), group=self.group)
        response = self.client.get(reverse('social:forum_home'), {'story_group_id': self.group.id})
        self.assertEqual(response.context['active_mode'], 'story')
        self.assertEqual(response.context['active_story_group'], self.group)
        self.assertIn('active_group_stories', response.context)

    def test_cleanup_command(self):
        """Test the management command"""
        from django.core.management import call_command
        
        story = Story.objects.create(user=self.user, image=self._make_image(), group=self.group)
        story.expires_at = timezone.now() - timedelta(hours=1)
        story.save()
        
        fresh_story = Story.objects.create(user=self.user, image=self._make_image(), group=self.group)
        
        call_command('cleanup_stories')
        
        self.assertEqual(Story.objects.count(), 1)
        self.assertEqual(Story.objects.first(), fresh_story)

    @classmethod
    def tearDownClass(cls):
        # Clean up test media directory
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()
