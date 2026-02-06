from django.test import TestCase
from django.contrib.auth import get_user_model

class UsersManagersTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email='normal@user.com', nickname='normaluser', password='foo')
        self.assertEqual(user.email, 'normal@user.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(ValueError):
            User.objects.create_user(email='')
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password="foo")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser('super@user.com', 'foo', nickname='superuser')
        self.assertEqual(admin_user.email, 'super@user.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='super@user.com', nickname='superuser_fail', password='foo', is_superuser=False)


class AutomaticPromotionTests(TestCase):
    """
    Tests pour la promotion automatique des utilisateurs au rôle de modérateur.
    Phase 2.5.1 : À niveau 50, l'utilisateur devient automatiquement modérateur.
    """
    
    def setUp(self):
        """Configuration commune pour tous les tests"""
        self.User = get_user_model()
    
    def test_user_below_level_50_not_promoted(self):
        """Test qu'un utilisateur de niveau 49 n'est pas promu"""
        user = self.User.objects.create_user(
            email='level49@test.com',
            nickname='Level49User',
            password='testpass'
        )
        user.xp = 4800  # 4800 // 100 + 1 = 49
        user.level = user.calculate_level()
        user.save()
        
        user.refresh_from_db()
        self.assertEqual(user.level, 49)
        self.assertFalse(user.role_moderator)
    
    def test_user_at_level_50_promoted(self):
        """Test qu'un utilisateur atteignant le niveau 50 est automatiquement promu"""
        user = self.User.objects.create_user(
            email='level50@test.com',
            nickname='Level50User',
            password='testpass'
        )
        user.xp = 4800  # Niveau 49
        user.level = user.calculate_level()
        user.save()
        
        # Ajouter XP pour atteindre le niveau 50
        user.add_xp(100)  # 4800 + 100 = 4900 = Niveau 50
        
        user.refresh_from_db()
        self.assertEqual(user.level, 50)
        self.assertTrue(user.role_moderator)
    
    def test_user_above_level_50_promoted(self):
        """Test qu'un utilisateur de niveau > 50 a le rôle de modérateur"""
        user = self.User.objects.create_user(
            email='level75@test.com',
            nickname='Level75User',
            password='testpass'
        )
        user.xp = 7400  # 7400 // 100 + 1 = 75
        user.level = user.calculate_level()
        user.save()
        
        user.refresh_from_db()
        self.assertEqual(user.level, 75)
        self.assertTrue(user.role_moderator)
    
    def test_already_moderator_no_toggle(self):
        """Test que le rôle de modérateur n'est pas basculé s'il est déjà True"""
        user = self.User.objects.create_user(
            email='already_mod@test.com',
            nickname='AlreadyMod',
            password='testpass'
        )
        user.role_moderator = True
        user.xp = 5000
        user.level = user.calculate_level()
        user.save()
        
        # Modifier autre chose pour trigger le signal
        user.bio = "Test bio"
        user.save()
        
        user.refresh_from_db()
        self.assertTrue(user.role_moderator)
    
    def test_update_role_based_on_level_method(self):
        """Test direct de la méthode update_role_based_on_level()"""
        user = self.User.objects.create_user(
            email='method_test@test.com',
            nickname='MethodTest',
            password='testpass'
        )
        
        # Niveau 49 : pas de promotion
        user.level = 49
        result = user.update_role_based_on_level()
        self.assertFalse(result)
        self.assertFalse(user.role_moderator)
        
        # Niveau 50 : promotion
        user.level = 50
        result = user.update_role_based_on_level()
        self.assertTrue(result)
        self.assertTrue(user.role_moderator)
        
        # Déjà modérateur : pas de changement
        result = user.update_role_based_on_level()
        self.assertFalse(result)
        self.assertTrue(user.role_moderator)
    
    def test_xp_progression_triggers_promotion(self):
        """Test d'intégration : add_xp() doit déclencher la promotion à niveau 50"""
        user = self.User.objects.create_user(
            email='xp_test@test.com',
            nickname='XPTest',
            password='testpass'
        )
        user.xp = 4800  # Niveau 49
        user.level = user.calculate_level()
        user.save()
        
        # Vérifier état initial
        self.assertEqual(user.level, 49)
        self.assertFalse(user.role_moderator)
        
        # Ajouter assez d'XP pour atteindre niveau 50
        user.add_xp(100)  # 4800 + 100 = 4900 = Niveau 50
        
        user.refresh_from_db()
        self.assertEqual(user.level, 50)
        self.assertTrue(user.role_moderator)

