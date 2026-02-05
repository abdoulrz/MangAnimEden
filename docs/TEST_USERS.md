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

---

### Comment réinitialiser ?

Si vous modifiez les mots de passe et souhaitez les remettre à défaut, exécutez :

```bash
python scripts/create_test_users.py
```
