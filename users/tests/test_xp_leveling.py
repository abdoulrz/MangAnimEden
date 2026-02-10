from django.test import TestCase
from django.contrib.auth import get_user_model
from reader.models import ReadingProgress
from catalog.models import Chapter, Series
from django.db import models

User = get_user_model()

class XPLevelingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            nickname='TestUser',
            password='password123',
            xp=0,
            level=0
        )
        self.series = Series.objects.create(title="Test Series")
        self.chapter = Chapter.objects.create(
            series=self.series,
            number=1,
            title="Chapter 1"
        )
    
    def test_calculate_level(self):
        """Test calculation of level based on XP."""
        # Level 0 (0-99 XP)
        self.user.xp = 0
        self.assertEqual(self.user.calculate_level(), 0)
        
        self.user.xp = 99
        self.assertEqual(self.user.calculate_level(), 0)
        
        # Level 1 (100-199 XP)
        self.user.xp = 100
        self.assertEqual(self.user.calculate_level(), 1)
        
        # Level 50 (5000 XP)
        self.user.xp = 5000
        self.assertEqual(self.user.calculate_level(), 50)
        
    def test_add_xp(self):
        """Test adding XP updates level."""
        self.user.xp = 95
        self.user.save()
        
        # Add 10 XP -> 105 XP -> Level 1
        self.user.add_xp(10)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.xp, 105)
        self.assertEqual(self.user.level, 1)

    def test_xp_award_on_chapter_completion(self):
        """Test that completing a chapter awards XP via signal."""
        initial_xp = self.user.xp
        
        # Create completed ReadingProgress
        ReadingProgress.objects.create(
            user=self.user,
            chapter=self.chapter,
            current_page=10,
            completed=True
        )
        
        self.user.refresh_from_db()
        # Should have gained 5 XP (as defined in signals.py)
        self.assertEqual(self.user.xp, initial_xp + 5)
        
    def test_automatic_moderator_promotion(self):
        """Test that reaching level 50 promotes user to moderator."""
        # Set user close to level 50 (4995 XP)
        self.user.xp = 4995
        self.user.level = 49
        self.user.role_moderator = False
        self.user.save()
        
        # Add 5 XP -> 5000 XP -> Level 50
        self.user.add_xp(5)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.level, 50)
        self.assertTrue(self.user.role_moderator)
        
    def test_get_level_progress(self):
        """Test level progress calculation."""
        self.user.xp = 150 # Level 1 (100-199)
        self.user.save()
        
        progress = self.user.get_level_progress()
        
        self.assertEqual(progress['current'], 150)
        self.assertEqual(progress['next'], 200)
        self.assertEqual(progress['percent'], 50.0) # 50/100 = 50%
