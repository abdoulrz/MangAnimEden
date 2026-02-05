# CHANGELOG

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

- Feature "Trending" dans la sidebar (actuellement placeholders statiques).
- Implémentation du système de "Stories" (en cours).

## [1.4.9] - 2026-02-05 ([Phase 2.5 - Profile Polish])

### Added Profile

- **Pages Domaine/Profile** : Fusion de l'expérience utilisateur. Le profil intègre désormais tous les blocs dynamiques du Domaine (Scans, Favoris, Stats, History).
- **Architecture SPA** : Navigation fluide intrabloc (Tabs) sans rechargement de page pour la section Domaine.
- **Statistiques** : Nouvelle logique "Séries terminées" (Calcul backend basé sur le ratio chapitres lus/total) + Empty States avec icônes.
- **UX** : Scrollbar customisée (Glassmorphism) pour les listes longues.

### Fixed

- **Stabilité** : Correction du crash si une série n'a pas de couverture (Placeholder automatique).
- **Design** : Ajustement des hauteurs max et du scrolling pour éviter les pages infinies.

## [1.4.8] - 2026-02-05 ([Phase 2.4 - Favoris])

### Added Favoris

- **Système de Favoris** : Possibilité d'ajouter des séries aux favoris via le bouton ❤️ sur la page de détail.
- **Domaine** : Nouvelle section "Mes Favoris" accessible depuis le dashboard utilisateur.
- **Page Détail** : Bouton favori dynamique avec état persisté et animation (AJAX).
- **Backend** : Modèle `Favorite` (User <-> Series) et vues associées.

### Fixed

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

### Changed

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
