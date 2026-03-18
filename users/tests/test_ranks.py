from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRankTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='ranktest@example.com',
            nickname='RankTester',
            password='password123',
            xp=0,
            level=1
        )

    def test_rank_data_exists(self):
        """Verify RANK_DATA is present in the User model."""
        self.assertTrue(hasattr(User, 'RANK_DATA'))
        self.assertEqual(len(User.RANK_DATA), 13)

    def test_get_rank_info_tier_1(self):
        """Test rank info for level 1 (Citoyen)."""
        self.user.level = 1
        rank = self.user.get_rank_info()
        self.assertEqual(rank['title'], 'Citoyen')
        self.assertEqual(rank['slug'], 'civilian')
        self.assertEqual(rank['emoji'], '🏘️')

    def test_get_rank_info_tier_5(self):
        """Test rank info for level 20 (Supernova)."""
        self.user.level = 20
        rank = self.user.get_rank_info()
        self.assertEqual(rank['title'], 'Supernova')
        self.assertEqual(rank['slug'], 'supernova')
        self.assertEqual(rank['emoji'], '🌟')

    def test_get_rank_info_tier_11(self):
        """Test rank info for level 65 (Commandant d'Empereur)."""
        self.user.level = 65
        rank = self.user.get_rank_info()
        self.assertEqual(rank['title'], "Commandant d'Empereur")
        self.assertEqual(rank['slug'], 'yonko-commander')
        self.assertEqual(rank['emoji'], '🎖️')

    def test_get_rank_info_max_tier(self):
        """Test rank info for level 100 (Monarque des Ombres)."""
        self.user.level = 100
        rank = self.user.get_rank_info()
        self.assertEqual(rank['title'], 'Monarque des Ombres')
        self.assertEqual(rank['slug'], 'shadow-monarch')
        self.assertEqual(rank['emoji'], '👑')

    def test_get_rank_info_beyond_limit(self):
        """Test rank info for level > 100."""
        self.user.level = 999
        rank = self.user.get_rank_info()
        self.assertEqual(rank['title'], 'Monarque des Ombres')
