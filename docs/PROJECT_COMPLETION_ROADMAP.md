# Roadmap de Finalisation du Projet : MangaAnimEden

Ce document trace la route logique pour emmener le projet de son état actuel jusqu'à la mise en production. Il est construit sur la base des documents existants (`DEBT.md`, `COMPLEX_IMPLEMENTATION_MEMO.md`, `DESIGN_SYSTEM.md`, `CHANGELOG.md`) et respecte la méthodologie stricte du `Guide Méthodologique.md`.

> **⚠️ RÈGLE D'OR (Spec-Driven Development)** :
> Aucune nouvelle fonctionnalité (Phase 2 & 3) ne doit être codée sans avoir d'abord créé sa spécification dans `docs/specs/` en utilisant `SPEC_TEMPLATE.md`.

---

## ✅ Phase 1 : Stabilisation et Dette Technique (COMPLÉTÉ)

*Avant d'ajouter de nouvelles fonctionnalités complexes, il faut solidifier les fondations pour éviter d'accumuler de la dette (cf. "Broken Windows").*

### 1.1 Gestion des Fichiers Statiques (Critique)

- [x] **Configurer `STATIC_ROOT`** dans `settings/prod.py`.
- [x] Mettre en place la commande `collectstatic`.
- [x] Vérifier que le CSS externe (récemment refactorisé) charge correctement sur toutes les pages.

### 1.2 Tests Unitaires (Critique)

- [x] **Créer `tests/` dans chaque app** (`core`, `catalog`, `reader`, `users`).
- [x] Écrire un test simple pour la vue `home` (sanity check).
- [x] Écrire test pour la création d'un utilisateur.
- [x] *Objectif : Éviter les régressions pendant la Phase 2.*

### 1.3 Nettoyage de l'Architecture

- [x] Vérifier que `Structure_frontend.js` sert bien de référence et n'est pas du code mort oublié à la racine.
- [x] Consolider les fichiers Markdown à la racine vers `docs/`.

---

## 🚀 Phase 2 : Complétion des Features "Core"

*Implémentation des fonctionnalités partiellement développées. Chaque item doit commencer par une Spec.*

### 2.1 Logique "Trending" (Catalogue Sidebar)

- [ ] **Spec** : Rédiger `docs/specs/SPEC-003-Trending-Logic.md`.
- [ ] **Backend** : Ajouter champ `views_count` ou modèle `DailyStat`.
- [ ] **Frontend** : Remplacer les placeholders statiques par une boucle dynamique.

### 2.2 Finalisation des "Stories" ✅ (COMPLÉTÉ)

- [x] **Spec** : Rédaction de `docs/specs/SPEC-004-Stories-Upload.md`.
- [x] **Feature** : Upload temporaire avec expiration 24h automatique.
- [x] **Refactoring** : Stories liées aux groupes (group-centric).
- [x] **Permissions** : Restriction publication aux modérateurs/admins.
- [x] **UI/UX** : Modal de sélection de groupe, carousel avec snap-to-center.
- [x] **Cleanup** : Suppression automatique des fichiers physiques.

### 2.3 Features Sociales Manquantes

- [ ] **Support Régional (Wisdom)** : Validation finale.
- [x] **Historique de Lecture** : Visualisation dans le Profil et le Domaine (ReadingProgress implémenté).

### 2.4 Gamification & Système de Gestion de Groupes

> **Objectif** : Lier la progression de lecture aux rôles utilisateurs et aux permissions de création/modération de groupes.

- [ ] **Spec** : Rédiger `docs/specs/SPEC-006-Gamification-Leveling.md`.
  
#### 2.4.1 Système de Niveaux (Leveling)

- [ ] **Backend - Calcul Automatique** :
  - [ ] Méthode `User.calculate_level()` : 10 chapitres lus = 1 niveau.
  - [ ] Signal/Hook pour recalculer le niveau après chaque chapitre lu.
  - [ ] Champ `User.current_level` (calculé ou cached).
  
- [ ] **Backend - Promotion Automatique** :
  - [ ] À niveau 50 (500 chapitres) : `User.role_moderator = True` automatiquement.
  - [ ] Signal `post_save` sur `User` pour mettre à jour les rôles.

#### 2.4.2 Système de Création de Groupes

- [ ] **Backend - Règles de Création** :
  - [ ] Exigence : 500 chapitres lus (niveau 50) pour créer un groupe.
  - [ ] Limite de groupes : `max_groups = level // 50` (niveau 50 = 1 groupe, niveau 100 = 2 groupes, etc.).
  - [ ] Ajouter champ `Group.owner` (ForeignKey vers User).
  - [ ] Validation dans `GroupCreateView` : vérifier niveau et quota.

- [ ] **Frontend - UI de Création** :
  - [ ] Bouton "Créer un Groupe" visible uniquement si niveau ≥ 50.
  - [ ] Message informatif si limite atteinte : "Niveau X requis pour créer plus de groupes".

#### 2.4.3 Permissions de Modération de Groupe

- [ ] **Backend - Permissions** :
  - [ ] Modèle `GroupMembership` avec champ `is_banned`.
  - [ ] Méthode `Group.ban_user(user)` / `unban_user(user)`.
  - [ ] Décorateur `@requires_group_moderator` pour vérifier `request.user == group.owner`.

- [ ] **Frontend - Actions Modérateur** :
  - [ ] Dans l'interface du groupe : bouton "Bannir" visible uniquement pour le propriétaire.
  - [ ] Stories : permission de publier réservée au propriétaire du groupe.

#### 2.4.4 Tests & Validation

- [ ] Tests unitaires pour `calculate_level()`.
- [ ] Tests d'intégration pour promotion automatique.
- [ ] Tests de validation des quotas de groupes.
- [ ] Tests de permissions de modération.

---

## 🛡️ Phase 3 : Sécurité et Intégrité (Complex Features)

*Basé sur `COMPLEX_IMPLEMENTATION_MEMO.md`. Ne pas négliger cette phase.*

### 3.1 Administration & Rôles

- [ ] **Spec** : Rédiger `docs/specs/SPEC-005-Admin-Dashboard.md`.
- [ ] **Middleware** : Décorateur `@requires_role`.
- [ ] **Audit Logs** : Modèle `SystemLog`.
- [ ] **Dashboard** : Page `/admin-panel/` avec Design System.

### 3.2 Gestion des Uploads (Sécurité)

- [ ] **Validateur** : Magic Bytes check pour les images.
- [ ] **Quotas** : Limites de taille par user.

### 3.3 Intégrité des Données

- [ ] **Cascades de Suppression** : Revoir les `on_delete` pour s'assurer que supprimer un User ne casse pas les discussions de groupe (passer en `SET_NULL` ou Soft Delete).

---

## 🎨 Phase 4 : UX, Polish et Design System

*Le "Wow Factor" demandé dans le `DESIGN_SYSTEM.md`.*

### 4.1 Unification Visuelle

- [ ] **Refactor** : Remplacer tout hexadécimal hardcodé par `var(--color-...)`.
- [ ] **Feedback** : Toasts pour succès/erreur.

### 4.2 Micro-Interactions

- [ ] **Animation** : Hover effects (Glassmorphism), Transitions de page.

---

## 🏁 Phase 5 : Préparation au Lancement (Release)

*Dernière ligne droite avant la Prod (Checklist "Flight Check").*

### 5.1 SEO & Meta

- [ ] `<meta>` descriptions dynamiques et Open Graph.

### 5.2 Performance & Deploy

- [ ] **Lazy Loading** : Vérification finale.
- [ ] **Images** : Format WebP.
- [ ] **Sécurité** : `SECRET_KEY`, `HTTPS`, `DEBUG=False`.
