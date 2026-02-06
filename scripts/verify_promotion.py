import os
import django
import sys
import traceback

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from catalog.models import Series, Chapter
from reader.models import ReadingProgress

User = get_user_model()

def verify_promotion():
    """
    Script de vérification de la promotion automatique.
    Phase 2.5.1 : Vérification que les utilisateurs sont automatiquement
    promus au rôle de modérateur lorsqu'ils atteignent le niveau 50.
    """
    try:
        print("=" * 70)
        print("VÉRIFICATION: Promotion Automatique (Phase 2.5.1)")
        print("=" * 70)
        
        # ===== Test 1: Utilisateur en dessous du niveau 50 =====
        print("\n--- Test 1: Utilisateur niveau 49 (pas de promotion) ---")
        email_49 = "promo_test_49@test.com"
        User.objects.filter(email=email_49).delete()
        
        user_49 = User.objects.create_user(
            email=email_49,
            password="testpass",
            nickname='PromoTest49'
        )
        user_49.xp = 4900  # Niveau 49
        user_49.level = user_49.calculate_level()
        user_49.save()
        
        user_49.refresh_from_db()
        print(f"Utilisateur créé: {user_49.nickname}")
        print(f"Niveau: {user_49.level}, XP: {user_49.xp}")
        print(f"Role Moderator: {user_49.role_moderator}")
        
        if user_49.level == 49 and not user_49.role_moderator:
            print("✅ SUCCÈS: Utilisateur niveau 49 n'est pas promu")
        else:
            print("❌ ÉCHEC: État incorrect pour utilisateur niveau 49")
        
        # ===== Test 2: Promotion à niveau 50 via add_xp =====
        print("\n--- Test 2: Promotion automatique à niveau 50 ---")
        email_50 = "promo_test_50@test.com"
        User.objects.filter(email=email_50).delete()
        
        user_50 = User.objects.create_user(
            email=email_50,
            password="testpass",
            nickname='PromoTest50'
        )
        user_50.xp = 4990  # Juste en dessous de niveau 50
        user_50.level = user_50.calculate_level()
        user_50.save()
        
        print(f"Utilisateur créé: {user_50.nickname}")
        print(f"État initial - Niveau: {user_50.level}, XP: {user_50.xp}, Moderator: {user_50.role_moderator}")
        
        # Ajouter XP pour atteindre niveau 50
        print("Ajout de 10 XP pour atteindre niveau 50...")
        user_50.add_xp(10)
        
        user_50.refresh_from_db()
        print(f"État final - Niveau: {user_50.level}, XP: {user_50.xp}, Moderator: {user_50.role_moderator}")
        
        if user_50.level == 50 and user_50.role_moderator:
            print("✅ SUCCÈS: Promotion automatique à niveau 50 fonctionne")
        else:
            print("❌ ÉCHEC: Promotion automatique n'a pas fonctionné")
        
        # ===== Test 3: Utilisateur au-dessus de niveau 50 =====
        print("\n--- Test 3: Utilisateur niveau 75 (promotion garantie) ---")
        email_75 = "promo_test_75@test.com"
        User.objects.filter(email=email_75).delete()
        
        user_75 = User.objects.create_user(
            email=email_75,
            password="testpass",
            nickname='PromoTest75'
        )
        user_75.xp = 7500  # Niveau 75
        user_75.level = user_75.calculate_level()
        user_75.save()
        
        user_75.refresh_from_db()
        print(f"Utilisateur créé: {user_75.nickname}")
        print(f"Niveau: {user_75.level}, XP: {user_75.xp}")
        print(f"Role Moderator: {user_75.role_moderator}")
        
        if user_75.level == 75 and user_75.role_moderator:
            print("✅ SUCCÈS: Utilisateur niveau 75 est automatiquement modérateur")
        else:
            print("❌ ÉCHEC: État incorrect pour utilisateur niveau 75")
        
        # ===== Test 4: Intégration complète avec ReadingProgress =====
        print("\n--- Test 4: Intégration avec ReadingProgress (500 chapitres) ---")
        email_integration = "promo_integration@test.com"
        User.objects.filter(email=email_integration).delete()
        
        user_integration = User.objects.create_user(
            email=email_integration,
            password="testpass",
            nickname='PromoIntegration'
        )
        
        print(f"Utilisateur créé: {user_integration.nickname}")
        print(f"État initial - Niveau: {user_integration.level}, XP: {user_integration.xp}, Moderator: {user_integration.role_moderator}")
        
        # Créer une série et des chapitres
        series_slug = "test-series-promo"
        if Series.objects.filter(slug=series_slug).exists():
            series = Series.objects.get(slug=series_slug)
        else:
            series = Series.objects.create(title="Test Series Promo", slug=series_slug)
        
        print(f"Simulation de lecture de 50 chapitres (50 * 10 XP = 500 XP = Niveau 50)...")
        
        # Simuler la lecture de 50 chapitres
        for i in range(1, 51):
            # Créer ou récupérer le chapitre
            chapter, _ = Chapter.objects.get_or_create(
                series=series,
                number=i,
                defaults={'title': f"Chapter {i}"}
            )
            
            # Créer ReadingProgress (déclenche le signal award_xp_on_read)
            ReadingProgress.objects.filter(user=user_integration, chapter=chapter).delete()
            ReadingProgress.objects.create(
                user=user_integration,
                chapter=chapter,
                completed=True
            )
        
        user_integration.refresh_from_db()
        print(f"État final - Niveau: {user_integration.level}, XP: {user_integration.xp}, Moderator: {user_integration.role_moderator}")
        
        if user_integration.level == 50 and user_integration.xp == 500 and user_integration.role_moderator:
            print("✅ SUCCÈS: Intégration complète fonctionne (ReadingProgress → XP → Niveau → Promotion)")
        else:
            print(f"❌ ÉCHEC: Intégration incomplète")
            print(f"   Attendu: Niveau 50, XP 500, Moderator True")
            print(f"   Obtenu: Niveau {user_integration.level}, XP {user_integration.xp}, Moderator {user_integration.role_moderator}")
        
        # ===== Résumé Final =====
        print("\n" + "=" * 70)
        print("RÉSUMÉ DE LA VÉRIFICATION")
        print("=" * 70)
        print("Tous les tests de promotion automatique ont été exécutés.")
        print("Vérifiez les résultats ci-dessus pour confirmer le bon fonctionnement.")
        
    except Exception:
        print("\n!!! EXCEPTION DÉTECTÉE !!!")
        traceback.print_exc()

if __name__ == '__main__':
    verify_promotion()
