# SPEC-009: Système de Badges (Achievements)

*Statut : Brouillon | Priorité : Moyenne**

## 1. Contexte & Intention ("The Why")

La gamification actuelle via les niveaux (XP) encourage la lecture continue. Cependant, elle ne récompense pas les jalons spécifiques ou les comportements diversifiés (ex: lire 10 séries différentes, commenter, être un membre actif d'un groupe).

Le système de badges vise à :

1. **Récompenser les accomplissements spécifiques** (e.g., "Premier Chapitre", "Marathonien").
2. **Augmenter la rétention** en donnant des objectifs à court/moyen terme.
3. **Enrichir le profil utilisateur** avec des éléments visuels de prestige.

## 2. Description du Produit ("The What")

### User Stories

* [ ] En tant que **Lecteur**, je veux recevoir une notification visible lorsque je débloque un badge.
* [ ] En tant que **Lecteur**, je veux voir la liste de mes badges sur mon profil.
* [ ] En tant que **Lecteur**, je veux voir les badges grisés (non obtenus) pour savoir ce qu'il me reste à accomplir (optionnel, peut être caché pour la surprise). *Décision: Afficher tous les badges, grisés si non acquis, avec condition visible.*

### Interface Utilisateur (UI)

* **Intégration Domaine (Espace Personnel)** :
  * **Navigation** : Le clic sur la "Glass Card" des badges redirige vers l'espace Domaine (`?mode=badges`). Pas de lien explicite requis dans la sidebar.
  * **Design Vertical (Timeline)** : Une barre de progression verticale linéaire représentant le "Chemin du Lecteur".
  * Les badges sont des nœuds sur cette ligne.
  * **Acquis** : Coloré, brillant, avec date d'obtention.
  * **Suivant** : Grisé mais visible (objectif).
  * **Futur** : Cadenassé ou mystérieux.
* Tooltip au survol pour voir la description précise et la condition.

* **Indicateurs** :
  * **Glass Card** : Compteur simple "Badges : X / Y".
  * **Notification** : Toast lors du déblocage.

## 3. Description Technique ("The How")

### Modèles de Données

```python
# users/models.py ou gamification/models.py (si nouvelle app, sinon users)
# Décision: Rester dans 'users' pour l'instant ou créer une app 'gamification' si ça grossit.
# Vu le roadmap, 'users' semble approprié ou une app dédiée 'achievements'.
# Restons simple : 'users' ou 'social' ? 'users' est le plus logique pour des attributs utilisateur.

class Badge(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/')
    
    # Logique d'attribution
    CONDITION_CHOICES = [
        ('CHAPTERS_READ', 'Chapitres Lus'),
        ('SERIES_COMPLETED', 'Séries Terminées'),
        ('COMMENTS_POSTED', 'Commentaires Postés'),
        ('ACCOUNT_AGE', 'Ancienneté (Jours)'),
        ('GROUP_JOINED', 'Groupes Rejoints'),
    ]
    condition_type = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    threshold = models.PositiveIntegerField(help_text="Valeur cible pour débloquer (ex: 100 pour 100 chapitres)")
    
    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    obtained_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'badge')
```

### Logique Métier (Service)

Créer un service `BadgeService` dans `users/services.py` :

* `check_badges(user, trigger_type)` : Méthode appelée par les signaux.
* Vérifie tous les badges du `trigger_type` que l'utilisateur n'a PAS encore.
* Si `user.stat >= badge.threshold`, créer `UserBadge` et retourner le badge pour notification.

### Signaux

Connecter les signaux existants au `BadgeService` :

* `post_save` sur `ReadingProgress` -> `check_badges(user, 'CHAPTERS_READ')`
* `post_save` sur `Comment` (à créer/vérifier) -> `check_badges(user, 'COMMENTS_POSTED')`

## 4. Critères de Validation ("Definition of Done")

* [ ] Modèles `Badge` et `UserBadge` créés et migrés.
* [ ] Fixtures initiales pour quelques badges de base (ex: "Novice" - 1 chapitre, "Fan" - 100 chapitres).
* [ ] Le service attribue correctement les badges rétroactivement ou au prochain événement.
* [ ] UI Profil affiche la grille des badges.
* [ ] Tests unitaires sur `BadgeService`.
