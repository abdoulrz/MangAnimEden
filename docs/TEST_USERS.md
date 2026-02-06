# Données Utilisateurs de Test

Ce fichier contient les identifiants pour les tests manuels.
Tous les mots de passe sont initialisés à : `password123`

## 1. Administrateur Site (Business Owner)

Cet utilisateur a accès au Dashboard complet.

- **Email** : `testadmin@example.com`
- **Pseudo** : `TestAdmin`
- **Mot de passe** : `password123`
- **Niveau** : 50
- **Rôles** : Admin, Modérateur, Lecteur

## 2. Modérateur

Cet utilisateur peut supprimer des messages mais n'a PAS accès au Dashboard Admin.

- **Email** : `testmod@example.com`
- **Pseudo** : `TestMod`
- **Mot de passe** : `password123`
- **Niveau** : 25
- **Rôles** : Modérateur, Lecteur

## 3. Utilisateur Normal

Utilisateur standard sans privilèges spéciaux.

- **Email** : `testnormal@example.com`
- **Pseudo** : `TestNormal`
- **Mot de passe** : `password123`
- **Niveau** : 5
- **Rôles** : Lecteur

## 4. Test Users - Phase 2.5.1 (Automatic Promotion)

Utilisateurs créés pour tester le système de promotion automatique.

### 4.1 PromoTest49 - Juste en dessous du seuil

- **Email** : `promo_test_49@test.com`
- **Pseudo** : `PromoTest49`
- **Mot de passe** : `testpass`
- **Niveau** : 49 (4800 XP)
- **Rôles** : Lecteur
- **Note** : N'a PAS le rôle modérateur (en dessous du niveau 50)

### 4.2 PromoTest50 - Au seuil de promotion

- **Email** : `promo_test_50@test.com`
- **Pseudo** : `PromoTest50`
- **Mot de passe** : `testpass`
- **Niveau** : 50 (4900 XP)
- **Rôles** : Lecteur, **Modérateur (automatique)**
- **Note** : Promu automatiquement au rôle modérateur à niveau 50

### 4.3 PromoTest75 - Au-dessus du seuil

- **Email** : `promo_test_75@test.com`
- **Pseudo** : `PromoTest75`
- **Mot de passe** : `testpass`
- **Niveau** : 75 (7400 XP)
- **Rôles** : Lecteur, **Modérateur (automatique)**
- **Note** : Promotion automatique confirmée pour les niveaux > 50

### 4.4 PromoIntegration - Test d'intégration complète

- **Email** : `promo_integration@test.com`
- **Pseudo** : `PromoIntegration`
- **Mot de passe** : `testpass`
- **Niveau** : 50 (500 XP via lecture de 50 chapitres)
- **Rôles** : Lecteur, **Modérateur (automatique)**
- **Note** : Promotion via le flow complet ReadingProgress → XP → Level → Auto-promotion

---

### Comment réinitialiser ?

Si vous modifiez les mots de passe et souhaitez les remettre à défaut, exécutez :

```bash
python scripts/create_test_users.py
```
