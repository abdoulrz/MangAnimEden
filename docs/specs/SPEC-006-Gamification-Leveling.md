# SPEC-006: Gamification & Leveling System

## 1. Vue d'ensemble

**Objectif** : Implémenter un système de gamification basé sur la progression de lecture pour encourager l'engagement communautaire et réguler la création/modération de groupes.

## 2. Règles du Système

### 2.1 Calcul des Niveaux

- **Formule** : `niveau = chapitres_lus // 10`
- Chaque 10 chapitres lus = 1 niveau gagné
- Exemples :
  - 0-9 chapitres → Niveau 0
  - 10-19 chapitres → Niveau 1
  - 500-509 chapitres → Niveau 50

### 2.2 Promotion Automatique

- **Niveau 50** (500 chapitres) → Promotion automatique à **Modérateur** (`role_moderator = True`)
- Cette promotion persiste même si le nombre de chapitres n'augmente plus

### 2.3 Création de Groupes

- **Prérequis** : Niveau 50 minimum (statut de modérateur)
- **Limite de groupes** : `max_groups = niveau // 50`
  - Niveau 50 → 1 groupe
  - Niveau 100 → 2 groupes
  - Niveau 150 → 3 groupes
  - etc.

### 2.4 Permissions de Modération

Les propriétaires de groupes (créateurs) peuvent :

- Publier des stories pour leur(s) groupe(s)
- Bannir/débannir des utilisateurs de leur(s) groupe(s)
- Modifier les paramètres de leur(s) groupe(s)

## 3. Modifications du Modèle

### 3.1 User (users/models.py)

**Nouveaux champs** :

```python
# Ajout d'un champ calculé ou cached
current_level = models.PositiveIntegerField(default=0, editable=False)

# Méthode pour recalculer le niveau
def calculate_level(self):
    from reader.models import ReadingProgress
    chapters_read = ReadingProgress.objects.filter(user=self).count()
    return chapters_read // 10

def update_level(self):
    new_level = self.calculate_level()
    if new_level != self.current_level:
        self.current_level = new_level
        # Auto-promotion à niveau 50
        if new_level >= 50 and not self.role_moderator:
            self.role_moderator = True
        self.save()
```

### 3.2 Group (social/models.py)

**Nouveaux champs** :

```python
owner = models.ForeignKey(
    settings.AUTH_USER_MODEL, 
    related_name='owned_groups', 
    on_delete=models.SET_NULL,
    null=True
)
```

**Validation** :

```python
def save(self, *args, **kwargs):
    if self.owner:
        # Vérifier le niveau
        if self.owner.current_level < 50:
            raise ValidationError("Niveau 50 requis pour créer un groupe")
        # Vérifier le quota
        owned_count = Group.objects.filter(owner=self.owner).count()
        max_allowed = self.owner.current_level // 50
        if owned_count >= max_allowed and not self.pk:  # Nouvelle création
            raise ValidationError(f"Limite atteinte : {max_allowed} groupe(s) autorisé(s)")
    super().save(*args, **kwargs)
```

### 3.3 GroupMembership (nouveau modèle)

```python
class GroupMembership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_banned = models.BooleanField(default=False)
    banned_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('group', 'user')
```

## 4. Signaux (Signals)

### 4.1 Mise à jour automatique du niveau

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from reader.models import ReadingProgress

@receiver(post_save, sender=ReadingProgress)
def update_user_level_on_progress(sender, instance, created, **kwargs):
    if created:
        instance.user.update_level()
```

## 5. Vues & Permissions

### 5.1 GroupCreateView

- Vérifier `request.user.current_level >= 50`
- Vérifier quota de groupes avant création
- Assigner automatiquement `owner = request.user`

### 5.2 StoryUploadView

- Vérifier que l'utilisateur est propriétaire du groupe cible
- Ou que l'utilisateur est admin/staff

### 5.3 BanUserView (nouveau)

- Vérifier que `request.user == group.owner`
- Créer/mettre à jour `GroupMembership.is_banned = True`
- Empêcher l'accès au groupe pour les utilisateurs bannis

## 6. Interface Utilisateur

### 6.1 Indicateur de Niveau

- Badge de niveau affiché sur le profil utilisateur
- Barre de progression vers le prochain niveau
- Indication du statut "Modérateur" si niveau ≥ 50

### 6.2 Page de Création de Groupe

- Bouton visible uniquement si niveau ≥ 50
- Message si limite atteinte : "Atteignez le niveau X pour créer plus de groupes"
- Compteur : "X/Y groupes créés"

### 6.3 Interface de Modération

- Dans la vue du groupe, bouton "⚙️ Modération" pour le propriétaire
- Liste des membres avec option "Bannir"
- Liste des membres bannis avec option "Débannir"

## 7. Tests Requis

### 7.1 Tests Unitaires

- `test_calculate_level_returns_correct_value()`
- `test_auto_promotion_at_level_50()`
- `test_group_creation_requires_level_50()`
- `test_group_quota_enforcement()`

### 7.2 Tests d'Intégration

- Lecture de 500 chapitres → vérifier promotion auto
- Création de multiple groupes → vérifier limite
- Bannissement d'utilisateur → vérifier accès refusé

## 8. Migration Plan

### Étape 1 : Préparer les modèles

- Ajouter `current_level` à User (migration)
- Ajouter `owner` à Group (migration avec SET_NULL pour groupes existants)
- Créer modèle `GroupMembership`

### Étape 2 : Data Migration

- Script pour recalculer les niveaux de tous les utilisateurs existants
- Script pour assigner un owner fictif (admin) aux groupes sans propriétaire

### Étape 3 : Implémenter les signaux

- Connecter le signal pour mise à jour automatique

### Étape 4 : Implémenter les vues & permissions

- Modifier GroupCreateView
- Ajouter validation dans StoryUploadView
- Créer BanUserView

### Étape 5 : Frontend

- Ajouter indicateurs de niveau
- Modifier UI de création de groupe
- Ajouter interface de modération

## 9. Risques & Considérations

### 9.1 Performance

- Le calcul de niveau via `count()` peut être coûteux → envisager cache/dénormalisation
- Indexer `GroupMembership.is_banned` pour requêtes rapides

### 9.2 UX

- Communiquer clairement les règles aux utilisateurs
- Afficher des tooltips/guides pour expliquer le système de niveaux

### 9.3 Migrations Existantes

- Les groupes créés avant cette feature n'auront pas de propriétaire → assigner admin par défaut

## 10. Chronologie d'Implémentation

**Estimé** : 2-3 sessions de développement

1. **Session 1** : Modèles, migrations, signaux (2h)
2. **Session 2** : Vues, permissions, décorateurs (2h)
3. **Session 3** : Frontend, tests, validation (2h)
