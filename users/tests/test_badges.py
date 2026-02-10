from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Badge, UserBadge
from reader.models import ReadingProgress
from catalog.models import Chapter, Series
from users.services import BadgeService

User = get_user_model()

class BadgeServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            nickname='TestUser',
            password='password123'
        )
        self.badge_novice = Badge.objects.create(
            name='Novice Reader',
            slug='novice-reader',
            description='Read 1 chapter',
            condition_type='CHAPTERS_READ',
            threshold=1,
            icon='badges/novice.png'
        )
        self.badge_expert = Badge.objects.create(
            name='Expert Reader',
            slug='expert-reader',
            description='Read 10 chapters',
            condition_type='CHAPTERS_READ',
            threshold=10,
            icon='badges/expert.png'
        )
        self.series = Series.objects.create(title="Test Series")
        self.chapters = []
        for i in range(10):
            self.chapters.append(Chapter.objects.create(
                series=self.series,
                number=i+1,
                title=f"Chapter {i+1}",
                source_file=f"chapter_{i+1}.pdf"
            ))

    def test_service_awards_badge(self):
        # User reads 1 chapter
        ReadingProgress.objects.create(
            user=self.user,
            chapter=self.chapters[0],
            current_page=10,
            completed=True
        )
        
        # Check badges
        BadgeService.check_badges(self.user, 'CHAPTERS_READ')
        
        # Should have Novice badge
        self.assertTrue(UserBadge.objects.filter(user=self.user, badge=self.badge_novice).exists())
        # Should NOT have Expert badge
        self.assertFalse(UserBadge.objects.filter(user=self.user, badge=self.badge_expert).exists())

    def test_signal_awards_badge(self):
        # Creating ReadingProgress should trigger signal
        ReadingProgress.objects.create(
            user=self.user,
            chapter=self.chapters[0],
            current_page=10,
            completed=True
        )
        
        # Signal should have called service
        self.assertTrue(UserBadge.objects.filter(user=self.user, badge=self.badge_novice).exists())

    def test_threshold_exact_match(self):
        # Read 10 chapters
        for i in range(10):
            ReadingProgress.objects.create(
                user=self.user,
                chapter=self.chapters[i],
                current_page=10,
                completed=True
            )
            
        # Should have both badges (signal triggers on each save)
        self.assertTrue(UserBadge.objects.filter(user=self.user, badge=self.badge_novice).exists())
        self.assertTrue(UserBadge.objects.filter(user=self.user, badge=self.badge_expert).exists())
