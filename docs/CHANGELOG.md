# CHANGELOG

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### To Be Implemented

- Phase 2.5.3: Système de Badges (Achievements)
- Phase 2.5.4: Système de Création de Groupes

## [1.9.1] - 2026-02-22 ([Phase 3.4 - Infrastructure & Storage])

### Changed Storage

- **Object Storage Migration** :
  - Migration complète depuis Cloudinary (stockage local éphémère de Render avec limites strictes) vers **Cloudflare R2** (S3-compatible).
  - Implémentation de `django-storages` avec le backend `S3Boto3Storage` pour remplacer la gestion des fichiers statiques et médias.
  - Transfert réussi et sans perte de plus de 4GB d'assets locaux existants (covers, backgrounds, avatars, scans .cbz/.cbr) vers le bucket R2 en garantissant zéro 404 en production.
  - Résolution du crash Git Push (`RPC failed; HTTP 500`) en expurgeant les uploads massifs de l'historique et de l'index Git (mise à jour propre du `.gitignore`).

## [1.9.0] - 2026-02-17 ([Phase 2.4.1 - Profile & UX Polish])

### Added Profile Features

- **Otaku Card** :
  - Nouvelle carte utilisateur "style carte de crédit" avec flip animation sur le profil.
  - Basculer entre la bannière classique et la carte via un bouton dédié.
- **Domaine Animation** :
  - Remplacement de l'animation de livre par défaut par une **Île Flottante**.
  - Animation CSS pure : Vagues rotatives (3 couches), île de terre et icône Torii (Statique).
- **Navigation Mobile & UX** :
  - **Grille Mobile** : Correction de la navbar (1x4) pour éviter le dépassement.
  - **Horizontal Scroll** : Panneaux "Amis" et "Badges" défilables horizontalement sur mobile avec snap-to-center.
  - **Inline Display** : Réorganisation des blocs latéraux (Amis/Badges) en mode horizontal sous le héros pour mobile.

### Changed Edit Profile

- **Redesign Complet** :
  - Suppression de la colonne "Aperçu" inutile pour centrer le formulaire.
  - Harmonisation des inputs et labels avec le Design System.
- **Light Mode Fixes** :
  - Correction critique : Textes blancs sur fond blanc (Labels, Placeholders) forcés en **Midnight Blue**.
  - Boutons d'action centrés sur mobile.

### Fixed General

- **Clean Up** : Suppression de la barre de recherche "Rechercher un manga" et du bloc "Compléter mon profil" une fois terminé.
- **Scrollbars** : Masquage des scrollbars disgracieuses dans la section Domaine et Listes.
- **Global Spacing** : Réduction des gaps excessifs sur mobile.

## [1.8.0] - 2026-02-10 ([Phase 3.2 - Notifications & Admin UI Polish])

### Added Notifications

- **Universal Notification System** :
  - **Backend** : Modèle `Notification` avec types (Like, Reply, System), service d'envoi et intégration des signaux.
  - **Universal Toast System** : Système de notifications flottantes (Toasts) non-intrusives avec glassmorphism et auto-dismiss.
  - **UI Dediee** : Page `/social/notifications/` redessinée et dropdown temps-réel dans la navbar.
- **Email System** : Intégration de `django.core.mail` pour l'envoi d'emails de bienvenue (Welcome Email) et réinitialisation de mot d'ordre (Password Reset).

### Changed Admin UI

- **Redesign des Genres** :
  - Cartes de genres avec glassmorphism, icônes FontAwesome et layout flexbox épuré.
  - Sélection des genres (Série) transformée en grille de "Chips" interactifs avec conteneur défilant.
- **Sidebar Navigation** : Correction de l'illumination de l'onglet actif pour toutes les vues d'administration.
- **Series List** : Suppression des badges redondants pour une interface plus propre.

### Fixed

- Correction des erreurs `NoReverseMatch` et `NameError` dans le système de notifications.

## [1.7.0] - 2026-02-09 ([Phase 3.3 - Upload Management & integrity])

### Added Upload

- **Series Folder Upload** : Possibilité d'uploader un dossier entier de chapitres lors de la création/édition d'une série.
- **Bulk Processing** : Création automatique des objets `Chapter` et extraction des pages via `FileProcessor`.
- **Large File Support** : Configuration optimisée pour supporter des uploads >1GB (via Waitress sur Windows).

### Changed Admin

- **Custom Admin Form** : Implementation d'un input HTML manuel pour contourner les limitations de validation Django sur les uploads de dossiers.

## [1.6.0] - 2026-02-08 ([Phase 3.1 - Google Auth & Integrity Roadmap])

### Added Auth

- **Google Authentication (OAuth2)** :
  - Intégration de `django-allauth` pour l'authentification sociale.
  - Configuration du provider Google avec scopes (email, profile).
  - **Custom Adapter** : `users/adapter.py` pour générer automatiquement un `nickname` unique à partir de l'email/nom Google (requis par notre modèle User).
  - Gestion des erreurs : Page `authentication_error.html` stylisée.
  - Simplification UX : `SOCIALACCOUNT_LOGIN_ON_GET = True` pour éviter l'écran intermédiaire.

### Added Documentation

- **Roadmap Refinement** :
  - Ajout de la **Phase 3.5 (Intégrité)** : Système de Signalement, Pages Légales, Vérification Email.
  - Ajout de la **Phase 5.3 (Passation Client)** : Checklist complète de transfert de propriété (Clés, Hébergement, Admin).
  - Ajout des tâches SEO (Sitemap) et Maintenance.
- **Scripts Utility** : `scripts/update_google_credentials.py` pour faciliter la mise à jour des clés API sans toucher au code ou à l'admin.

## [1.4.18] - 2026-02-06 ([Phase 2.5.2 - Friendship System])

### Added - Système Social (Amis)

- **Friendship Model & Backend**
  - Nouveau modèle `Friendship` avec gestion des statuts (pending/accepted)
  - Migration `0004_friendship` avec contraintes d'unicité
  - 6 nouvelles méthodes User: `get_friends()`, `get_friend_count()`, `get_pending_requests()`, `is_friend_with()`, `has_pending_request_from()`, `has_sent_request_to()`
  - 5 vues friendship: envoyer, accepter, refuser, retirer demandes + API JSON liste d'amis
  - Routage URL pour toutes les opérations d'amitié (`/forum/friends/*`)
  - Intégration Django admin pour gestion des amitiés

- **Profils Publics**
  - Nouvelle vue profil public à `/users/user/<id>/`
  - Bouton action ami dynamique avec 4 états: "Ajouter en ami", "Demande envoyée", "Accepter la demande", "Amis"
  - Affichage statistiques publiques (niveau, XP, amis, chapitres, séries)
  - Redirection automatique vers profil privé si consultation de soi-même

- **Découverte d'Amis**
  - Pseudos cliquables dans les messages de chat de groupe
  - Liens directs des messages vers profils publics
  - Flux de découverte: Chat → Profil → Ajouter Ami

- **Améliorations Profil Privé**
  - Panneau amis pliable avec design glassmorphique
  - Section demandes en attente avec boutons Accepter/Refuser
  - Liste d'amis chargée via AJAX
  - Compteur d'amis dynamique avec badge demandes en attente
  - Animations fluides pour mises à jour en temps réel

- **Tests**
  - 13 tests unitaires complets pour modèle Friendship
  - Couverture cas limites: doublons, auto-amitié, relations bidirectionnelles
  - Toutes les méthodes friend User testées

### Fixed

- Barre XP apparaissant pleine à faibles pourcentages sur profils publics
- Pseudos chat affichant texte littéral template (problème variable template multiligne)
- Problèmes cache template résolus avec mises à jour STATIC_VERSION

## [1.5.5] - 2026-02-07 ([Phase 2.5.3 - Badges System])

### Added Badges

- **Système de Badges (Achievements)** :
  - **Backend** : Modèles `Badge` et `UserBadge` pour gérer les succès.
  - **Service** : `BadgeService.check_badges()` évalue les conditions (ex: "Chapitres Lus").
  - **Automation** : Intégration dans `users/signals.py` pour déblocage temps réel.
  - **UI Profil** : Timeline verticale (Glassmorphism) interfacée avec le système "Domaine".
  - **Design** : Icônes "Bulb" (64px) et indicateurs d'état (Verrouillé/Débloqué/Prochain).

### Changed XP

- **Rééquilibrage** : Gain d'XP réduit de 10 à **5 XP** par chapitre pour une progression plus durable.

### Fixed Duplication XP

- **Duplication XP** : Correction d'un bug dans le lecteur où rafraîchir la page attribuait l'XP plusieurs fois.
- **Navigation Profil** : Correction du Routing JS pour les onglets du Domaine (Badges, Stats, etc.) fonctionnant comme une SPA.

## [1.5.4] - 2026-02-07 ([Phase 2.5.4 & 2.5.5 - Group Logic & UI])

### Added Groups

- **Création de Groupe (Restriction)** :
  - Limité aux utilisateurs de **Niveau 50+** (500 chapitres lus).
  - Quota de création : 1 groupe tous les 50 niveaux (`level // 50`).
  - Validation backend stricte dans `GroupCreateView`.
- **Modération de Groupe** :
  - Le créateur du groupe est désigné automatiquement comme **Propriétaire**.
  - Possibilité pour le propriétaire de **bannir/débannir** des membres via le chat.
  - Modèle `GroupMembership` pour gérer les statuts (banni, membre).
- **UI Premium** :
  - **Page Création** : Refonte totale avec design "Glassmorphism Premium", upload d'image stylisé et prévisualisation.
  - **Sidebar Forum** : Nouveau bouton "+" stylisé pour l'ajout de groupe (visible uniquement si éligible).
  - **Formulaires** : Création de `forms.css` pour une stylisation unifiée et moderne des inputs.

### Changed

- **Forum Sidebar** : Affichage conditionnel du bouton de création de groupe.
- **Chat** : Bouton de bannissement visible uniquement pour le propriétaire du groupe sur les messages des autres membres.

## [1.5.2] - 2026-02-06 ([Phase 2.5.1 - Automatic Promotion])

### Added Automatic Promotion

- **Promotion Automatique** : Les utilisateurs atteignant **niveau 50** (500 chapitres lus) sont automatiquement promus au rôle de **Modérateur**.
- **Backend Logic** : Nouvelle méthode `User.update_role_based_on_level()` pour vérifier et mettre à jour les rôles basés sur le niveau.
- **Django Signal** : `check_and_promote_user` dans `users/signals.py` - Déclenche automatiquement la promotion lors de la sauvegarde d'un utilisateur.
- **Prévention Récursion** : Utilisation de `update_fields=['role_moderator']` pour éviter les boucles infinies.
- **Tests Unitaires** : Suite de 6 tests automatisés dans `users/tests/test_models.py` (AutomaticPromotionTests) :
  - Test utilisateur niveau 49 (pas de promotion)
  - Test utilisateur niveau 50 (promotion automatique)
  - Test utilisateur niveau > 50 (promotion garantie)
  - Test utilisateur déjà modérateur (pas de toggle)
  - Test méthode `update_role_based_on_level()`
  - Test intégration XP → Level → Promotion
- **Scripts de Vérification** : `scripts/verify_promotion.py` pour validation manuelle et démonstration.

### Technical Details

- **Formule Niveau** : `Level = (XP // 100) + 1`
- **Seuil Promotion** : Niveau 50 = 4900-4999 XP
- **Flow Complet** : ReadingProgress (completed) → Signal XP → User.add_xp() → Level Update → Signal Promotion → role_moderator = True

## [1.5.1] - 2026-02-06 ([Phase 2.5 - Gamification System])

### Added Gamification

- **Système XP & Niveaux** : Les utilisateurs gagnent **10 XP par chapitre lu**.
- **Calcul Automatique** : `User.calculate_level()` (Niveau = XP // 100 + 1).
- **Django Signal** : `users/signals.py` - Attribution automatique d'XP lors de la complétion d'un chapitre.
- **Profile UI** : Badge de niveau dynamique et barre de progression XP (Glass Card design).
- **Backend Methods** : `add_xp()`, `get_level_progress()` pour gestion et affichage temps réel.

### Fixed Reader

- **Bug Critique** : Les chapitres lus n'étaient pas marqués `completed=True`, empêchant l'attribution d'XP.
- **Solution** : Ajout de `defaults={'completed': True}` dans `reader/views.py` (`update_or_create`).
- **Migration Données** : Script de réparation rétroactif pour accorder XP manquant aux utilisateurs existants.

### Changed UX

- **Favicon** : Icône Torii Gate (⛩️) pour refléter le thème "Eden/Gateway".
- **Navbar** : Remplacement de l'icône pile de livres par Torii Gate.
- **Avatar Utilisateur** : Correction de l'initiale (affichage du `nickname` au lieu de "N").
- **Catalogue** : Tri alphabétique (A-Z) des séries au lieu du tri par "Dernière mise à jour".

## [1.5.0] - 2026-02-05 ([Phase 2.3 - Wisdom & UX Polish])

### Added Wisdom

- **Feature "Wisdom" (Support Régional)** : Base de données client-side (`app.js`) de citations inspirantes (Manga, Manhwa, Manhua).
- **Localization** : Traduction intégrale des citations en Français.
- **Performance** : Suppression de l'appel API bloquant vers `animechan.xyz`.

### Changed Design

- **Hero Banner Redesign** :
  - **Compact Mode** : Bannière réduite (~100px) pour les utilisateurs connectés ("Reprendre la lecture").
  - **Guest Mode** : Teaser "Prochainement" pour les fonctionnalités sociales (Groupes/Niveaux).
- **Ambiance** : Ajout de gradients d'arrière-plan "Ambient" (Violet/Rose) pour réchauffer l'interface sombre.
- **Spacing** : Réduction significative de l'espace entre le Hero et la grille de contenu.

### Added Docs

- **Mobile Strategy** : Nouvelle section "Mobile First" dans `DESIGN_SYSTEM.md`.

## [1.4.9] - 2026-02-05 ([Phase 2.5 - Profile Polish])

### Added Profile

- **Pages Domaine/Profile** : Fusion de l'expérience utilisateur. Le profil intègre désormais tous les blocs dynamiques du Domaine (Scans, Favoris, Stats, History).
- **Architecture SPA** : Navigation fluide intrabloc (Tabs) sans rechargement de page pour la section Domaine.
- **Statistiques** : Nouvelle logique "Séries terminées" (Calcul backend basé sur le ratio chapitres lus/total) + Empty States avec icônes.
- **UX** : Scrollbar customisée (Glassmorphism) pour les listes longues.

### Fixed Profile

- **Stabilité** : Correction du crash si une série n'a pas de couverture (Placeholder automatique).
- **Design** : Ajustement des hauteurs max et du scrolling pour éviter les pages infinies.

## [1.4.8] - 2026-02-05 ([Phase 2.4 - Favoris])

### Added Favoris

- **Système de Favoris** : Possibilité d'ajouter des séries aux favoris via le bouton ❤️ sur la page de détail.
- **Domaine** : Nouvelle section "Mes Favoris" accessible depuis le dashboard utilisateur.
- **Page Détail** : Bouton favori dynamique avec état persisté et animation (AJAX).
- **Backend** : Modèle `Favorite` (User <-> Series) et vues associées.

- **Navigation** : Suppression de "Mes Favoris" du menu dropdown (maintenant dans Domaine).
- **URL Routing** : Correction du path API pour les favoris (`/catalogue/` vs `/catalog/`).
- **CSRF** : Implémentation robuste de `getCookie` pour les requêtes AJAX.
- **UI** : Centrage des titres et ajout d'états vides animés (Scans, Favoris).

## [1.3.0] - 2026-02-04 ([Phase 1 Completed])

### Added Tests

- **Unit Tests** : Structure de tests (`tests/`) pour `core`, `catalog`, `reader`, `users`. Ajout de sanity checks pour la Home et la création d'User.

### Fixed Static

- **Static Files** : Configuration de `STATIC_ROOT` et validation de `collectstatic`.
- **Architecture** : Nettoyage des fichiers racine et consolidation dans `docs/`.

## [1.2.0] - 2026-02-04

### Added Dashboard

- **Admin Dashboard** (`/users/admin-panel/`) : Interface dédiée pour les administrateurs "Business".
  - Gestion des utilisateurs (Tableau, Rôles, Statut Ban).
  - Gestion du contenu (Redirection vers Django Admin pour les Séries).
  - Protection via décorateurs `@requires_admin`.
- **Rôles Utilisateurs** : Ajout des champs `role_admin`, `role_moderator`, `is_banned` au modèle User.
- **Modération** : Fonctionnalité de suppression de message pour les modérateurs (`@requires_moderator`).
- **Design Ops** : Création de `TEST_USERS.md` et script `create_test_users.py` pour la gestion des comptes de test.

### Fixed fichiers

- **CSS** : Correction du chargement des fichiers statiques sur les routes imbriquées (Fix `STATIC_URL` en absolu).
- **Catalogue** : Correction du lien brisé (`NoReverseMatch`) en remplaçant les cartes statiques par une boucle dynamique sur la DB.

## [1.1.0] - 2026-02-02

### Added Refonte

- **Refonte UI Complète** : Adoption du design "Purple/Dark Premium" (Neumorphism & Glassmorphism).
- **Design System** : Création de `tokens.css` et `components.css`.
- **Navbar** : Nouvelle barre de navigation responsive avec flou (Glassmorphism), recherche et avatar utilisateur.
- **Page Profil** : Edition du profil avec prévisualisation live de l'avatar.
- **Catalogue** : Grille de mangas avec cartes stylisées (Cover, Badges, Rating).

### Changed Designs

- Remplacement de tout le CSS inline par des fichiers CSS externes (`auth.css`, `admin.css`, `pages.css`).
- Architecture des templates Django : Meilleure utilisation de `base.html` et des blocks.

## [1.0.0] - 2026-01-20

### Added Release

- **Initial Release** : Lancement du MVP MangaAnimEden.
- **Apps** : `core`, `users`, `catalog`, `reader`, `social`.
- **Reader** : Lecteur de manga basique (navigation chapitre/page).
- **Auth** : Système d'inscription et de connexion personnalisé.
- **Social** : Chat en temps réel (Websockets/Polling basique) et Groupes.

## [0.1.0] - 2026-01-15

### Added Initialisation

- Initialisation du projet Django `MangaAnimEden` (basé sur un squelette Inventory App).
- Configuration de la base de données SQLite.
- Structure des dossiers (`apps/`, `config/`, `static/`, `templates/`).
