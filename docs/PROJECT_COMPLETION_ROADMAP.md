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

### 2.1 Logique "Trending" (Catalogue Sidebar) ✅ (COMPLÉTÉ)

- [x] **Spec** : Rédiger `docs/specs/SPEC-003-Trending-Logic.md`.
- [x] **Backend** : Ajouter champ `views_count` ou modèle `DailyStat`.
- [x] **Frontend** : Remplacer les placeholders statiques par une boucle dynamique.

### 2.2 Finalisation des "Stories" ✅ (COMPLÉTÉ)

- [x] **Spec** : Rédaction de `docs/specs/SPEC-004-Stories-Upload.md`.
- [x] **Feature** : Upload temporaire avec expiration 24h automatique.
- [x] **Refactoring** : Stories liées aux groupes (group-centric).
- [x] **Permissions** : Restriction publication aux modérateurs/admins.
- [x] **UI/UX** : Modal de sélection de groupe, carousel avec snap-to-center.
- [x] **Cleanup** : Suppression automatique des fichiers physiques.

### 2.3 Features Sociales Manquantes

- [x] **Support Régional (Wisdom)** : Validation finale.
- [x] **Historique de Lecture** : Visualisation dans le Profil et le Domaine (ReadingProgress implémenté).

### 2.4 Retours Utilisateurs & Fixes (URGENT)

*Corrections immédiates et ajustements UX demandés.*

#### 2.4.1 Nettoyage & Redondance

- [ ] **Suppression Page Domaine** : Rediriger `/domaine/` vers `/profile/` (section intégrée). Supprimer le code mort.
- [ ] **Profil** : Supprimer le bloc "Paramètres du profil" (doublon ou inutile).
- [ ] **Profil Redesign** : Refondre le bloc "Info Utilisateur" (Niveau, Amis) pour un look plus premium.

#### 2.4.2 Navigation & Footer

- [ ] **Footer Global** :
  - [ ] Lien "Catalogue" -> `/catalogue/`.
  - [ ] Lien "Conditions" -> `/about/#conditions`.
  - [ ] Remplacer "Contact" par "About" (Fondateurs, Histoire, Objectifs).
- [ ] **Page Détail** :
  - [ ] Bouton Retour : "Retour à l'accueil" -> "Retour au Catalogue".
  - [ ] Tabs : Réparer les boutons Info/Avis qui ne fonctionnent plus.
  - [ ] Liste Chapitres : Afficher 10 chapitres max + Scroll infini/Load more dans un container stylisé.

#### 2.4.3 Fonctionnalités "Quick Wins"

- [ ] **Forum** : Réparer le bouton "Ajouter une Story".
- [ ] **Thème** : Activer la logique du Theme Switcher (bouton existant).

### 2.5 Gamification & Système de Gestion de Groupes

> **Objectif** : Lier la progression de lecture aux rôles utilisateurs et aux permissions de création/modération de groupes.

- [ ] **Spec** : Rédiger `docs/specs/SPEC-006-Gamification-Leveling.md`.
  
#### 2.5.1 Système de Niveaux (Leveling & XP)

- [ ] **Backend - Logique XP** :
  - [ ] **Signal** : Créer un signal (sur lecture de chapitre) pour attribuer de l'XP (+10 XP / chapitre).
  - [ ] **Calcul** : Méthode `User.calculate_level()` basée sur l'XP total.
  - [ ] **View** : Mettre à jour `profile_view` pour injecter les vraies données (XP actuel, Next Level XP, Barre de progression) au template.
  
- [ ] **Backend - Promotion Automatique** :
  - [ ] À niveau 50 (500 chapitres) : `User.role_moderator = True` automatiquement.
  - [ ] Signal `post_save` sur `User` pour mettre à jour les rôles.

#### 2.5.2 Système Social (Amis)

- [ ] **Backend - Gestion des Amis** :
  - [ ] Modèle `Friendship` (Demandeur, Receveur, Statut: Pending/Accepted).
  - [ ] Logique : Envoyer demande, Accepter, Refuser, Retirer.
  - [ ] Compteurs : Méthode pour compter les amis actifs.
- [ ] **Frontend - UI Sociale** :
  - [ ] Profil Public : Bouton "Ajouter en ami" / "Demande envoyée".
  - [ ] Profil Privé : Liste des amis et compteur dans la "Glass Card".

#### 2.5.3 Système de Badges (Achievements)

- [ ] **Backend - Gestion des Badges** :
  - [ ] Modèle `Badge` (Nom, Icone, Condition, Slug).
  - [ ] Modèle `UserBadge` (Liaison User-Badge avec date d'obtention).
  - [ ] Service d'attribution : Vérifier les règles (e.g. "Premier Chapitre", "100 Chapitres") et débloquer.
- [ ] **Frontend - UI Badges** :
  - [ ] Affichage du compteur de badges dans la "Glass Card".
  - [ ] Grille des badges obtenus sur le profil.

#### 2.5.4 Système de Création de Groupes

- [ ] **Backend - Règles de Création** :
  - [ ] Exigence : 500 chapitres lus (niveau 50) pour créer un groupe.
  - [ ] Limite de groupes : `max_groups = level // 50` (niveau 50 = 1 groupe, niveau 100 = 2 groupes, etc.).
  - [ ] Ajouter champ `Group.owner` (ForeignKey vers User).
  - [ ] Validation dans `GroupCreateView` : vérifier niveau et quota.

- [ ] **Frontend - UI de Création** :
  - [ ] Bouton "Créer un Groupe" visible uniquement si niveau ≥ 50.
  - [ ] Message informatif si limite atteinte : "Niveau X requis pour créer plus de groupes".

#### 2.5.5 Permissions de Modération de Groupe

- [ ] **Backend - Permissions** :
  - [ ] Modèle `GroupMembership` avec champ `is_banned`.
  - [ ] Méthode `Group.ban_user(user)` / `unban_user(user)`.
  - [ ] Décorateur `@requires_group_moderator` pour vérifier `request.user == group.owner`.

- [ ] **Frontend - Actions Modérateur** :
  - [ ] Dans l'interface du groupe : bouton "Bannir" visible uniquement pour le propriétaire.
  - [ ] Stories : permission de publier réservée au propriétaire du groupe.

#### 2.5.6 Tests & Validation

- [ ] Tests unitaires pour XP et Leveling.
- [ ] Tests d'intégration pour le système d'Amis et Badges.
- [ ] Tests de validation des quotas de groupes.
- [ ] Tests de permissions de modération.

## 🛡️ Phase 3 : Sécurité, Auth & Intégrité

*Basé sur `COMPLEX_IMPLEMENTATION_MEMO.md`. Ne pas négliger cette phase.*

### 3.1 Authentification & Rôles

- [ ] **Google Auth** : Inscription/Connexion via Google (OAuth2).
- [ ] **Spec** : Rédiger `docs/specs/SPEC-005-Admin-Dashboard.md`.
- [ ] **Middleware** : Décorateur `@requires_role`.
- [ ] **Audit Logs** : Modèle `SystemLog`.
- [ ] **Dashboard** : Page `/admin-panel/` avec Design System.
  - [ ] **Gestion Complète** : Permettre aux admins/staff de gérer entièrement le contenu (séries/chapitres) et les utilisateurs (clés/rôles/bans) sans passer par l'interface Django Admin standard.

### 3.2 Notifications & Social

- [ ] **Système de Notifications** :
  - [ ] Backend : Modèle `Notification` (Type: Like, Reply, System).
  - [ ] UI : Dropdown (5 dernières) + Page dédiée "Toutes les notifications".
  - [ ] Realtime : Polling ou Websocket.

### 3.3 Gestion des Uploads (Sécurité)

- [ ] **Validateur** : Magic Bytes check pour les images.
- [ ] **Quotas** : Limites de taille par user.

### 3.4 Recherche Avancée

- [ ] **Moteur de Recherche** :
  - [ ] UI : Présentation des résultats (Live search vs Page de résultats).
  - [ ] Backend : Filtres (Genre, Statut, Auteur) et Tri.

### 3.5 Intégrité des Données

- [ ] **Cascades de Suppression** : Revoir les `on_delete` pour s'assurer que supprimer un User ne casse pas les discussions de groupe (passer en `SET_NULL` ou Soft Delete).

### 3.6 Support Multi-Formats (CBR, CBZ, PDF, EPUB)

- [ ] **Spec** : Rédiger `docs/specs/SPEC-007-Multi-Format-Reader.md`.
- [ ] **Backend** :
  - [ ] Support des archives (CBR/CBZ) : Extraction via `zipfile`/`rarfile`.
  - [ ] Support PDF : Conversion en images via `pdf2image` ou extraction.
  - [ ] Support EPUB : Parsing via `EbookLib`.
  - [ ] Modèle `Chapter` : Ajouter champ générique `source_file` et `format_type`.
- [ ] **Frontend** :
  - [ ] Reader unifié (Canvas ou IMG tags).
  - [ ] Gestion du chargement progressif (Streaming/Lazy Loading).

---

## 🎨 Phase 4 : UX, Polish et Design System

*Le "Wow Factor" demandé dans le `DESIGN_SYSTEM.md`.*

### 4.1 Unification Visuelle

- [ ] **Refactor** : Remplacer tout hexadécimal hardcodé par `var(--color-...)`.
- [ ] **Feedback** : Toasts pour succès/erreur.

### 4.2 Micro-Interactions

- [ ] **Animation** : Hover effects (Glassmorphism), Transitions de page.
- [ ] **Mobile Touch** : Feedback visuel au tap (:active), Swipe gestures.

### 4.3 Mobile Experience (Prioritaire)

- [ ] **Responsive Check** : Vérification des grilles et tailles de police sur < 400px.
- [ ] **Touch Targets** : Audit des boutons trop petits.
- [ ] **Navigation** : Test du menu sur mobile (Burger ou Bottom Nav).

---

## 🏁 Phase 5 : Préparation au Lancement (Release)

*Dernière ligne droite avant la Prod (Checklist "Flight Check").*

### 5.1 SEO & Meta

- [ ] `<meta>` descriptions dynamiques et Open Graph.

### 5.2 Performance & Deploy

- [ ] **Lazy Loading** : Vérification finale.
- [ ] **Images** : Format WebP.
- [ ] **Sécurité** : `SECRET_KEY`, `HTTPS`, `DEBUG=False`.
