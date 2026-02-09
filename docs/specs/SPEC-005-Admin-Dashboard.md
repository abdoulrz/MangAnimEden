# Admin Dashboard & Governance Spec

* **Titre :** Admin Dashboard & Governance
* **Statut :** Brouillon
* **Priorité :** Haute

## 1. Contexte & Intention ("The Why")

Actuellement, l'administration du site repose soit sur l'interface Django Admin (trop technique et dangereuse pour des modérateurs métier), soit sur des accès directs en base de données.
Il est critique de fournir une interface "Business" (`/admin-panel/`) permettant aux propriétaires du site et modérateurs de gérer la communauté et le contenu sans risques technique, et avec une UX cohérente avec le reste du site (Neumorphism).
De plus, pour des raisons de sécurité et d'audit, toutes les actions sensibles (bannissement, suppression de contenu) doivent être logguées.

## 2. Description du Produit ("The What")

Une nouvelle section du site, accessible uniquement aux utilisateurs ayant `role_admin=True` ou `role_moderator=True`.

### User Stories

* [ ] En tant qu'**Admin**, je veux voir une vue d'ensemble de l'activité du site (Nouveaux inscrits, rapports en attente).
* [ ] En tant que **Modérateur**, je veux pouvoir chercher un utilisateur par pseudo/email et voir son statut (Actif/Banni).
* [ ] En tant que **Modérateur**, je veux pouvoir bannir un utilisateur avec une raison, et que cette action soit enregistrée.
* [ ] En tant qu'**Admin**, je veux voir l'historique des actions de modération (Logs) pour vérifier les abus de pouvoir.
* [ ] En tant qu'**Admin**, je veux gérer les séries, genres et chapitres (CRUD complet) sans passer par Django Admin.
* [ ] En tant qu'**Admin**, je veux pouvoir fermer un Groupe public qui enfreint les règles.

### Interface (UI/UX)

* **Design** : Utilisation du Design System existant (Glassmorphism/Neumorphism).
* **Sidebar** : Navigation spécifique à l'admin (Dashboard, Users, Content, Reports, Logs).
* **Tableaux** : Listes avec filtres et pagination pour les utilisateurs et logs.

### Sécurité & Accès

* **Stealth Mode** : Si un utilisateur non-autorisé tente d'accéder à `/admin-panel/`, il doit recevoir une erreur **404 Not Found** (et non une 403), pour masquer l'existence de l'interface d'administration.

## 3. Description Technique ("The How")

### 3.1 Nouvelle Application

Création d'une app Django dédiée : `administration`.

### 3.2 Modèles de Données

#### `SystemLog`

Pour l'audit trail.

```python
class SystemLog(models.Model):
    ACTION_TYPES = [
        ('USER_BAN', 'Bannissement Utilisateur'),
        ('USER_UNBAN', 'Débannissement Utilisateur'),
        ('CONTENT_DELETE', 'Suppression Contenu'),
        ('ROLE_CHANGE', 'Changement de Rôle'),
        # ...
    ]
    actor = models.ForeignKey(User, related_name='actions_performed', ...)
    target_user = models.ForeignKey(User, related_name='actions_received', null=True, blank=True, ...)
    action = models.CharField(choices=ACTION_TYPES, ...)
    details = models.TextField(blank=True) # JSON ou Text pour détails
    ip_address = models.GenericIPAddressField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 3.3 Middleware / Décorateurs

Implémentation de `@requires_role(role_name)` qui lève `Http404` si l'utilisateur n'a pas le rôle requis.

### 3.4 Vues Clés

* `AdminDashboardView`: KPIs (Statistiques).
* `UserListView` & `UserDetailView`: Recherche et actions (Ban/Promote).
* `SystemLogListView`: Historique des actions.
* `SeriesListView`, `SeriesCreateView`, `SeriesUpdateView`: Gestion du catalogue (CRUD).
* `ChapterListView` (par Série), `ChapterCreateView`: Gestion des chapitres.
* `GenreListView`, `GenreCreateView`: Gestion des taxonomies.
* `GroupListView`, `GroupUpdateView`: Modération des communautés.

## 4. Critères de Validation (Checklist)

* [ ] Un utilisateur non-staff recevant une **404** en tentant d'accéder à `/admin-panel/`.
* [ ] Une action de bannissement crée une entrée dans `SystemLog`.
* [ ] Le dashboard s'affiche correctement avec le design system actuel.
* [ ] Les formulaires de gestion de contenu (Séries) fonctionnent et permettent de créer/modifier des séries.
* [ ] Les tests unitaires couvrent les permissions et la création de logs.
