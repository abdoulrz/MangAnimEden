# CHANGELOG

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### To Be Implemented

- Phase 3.6 : Support Client (Formulaire de Contact)
- Phase 3.7 : Monétisation & Publicité
- Phase 4 : UX Polish & Design System Unification
- Phase 5 : SEO, Performance & Lancement

---

## [2.4.0] - 2026-03-18 ([Forum UX Refinement & Icon Excellence])

### Added
- **Forum UI/UX (Phase 5 Refinement)** :
  - **Friends Dropdown** : Nouveau menu déroulant glassmorphique dans l'en-tête de la sidebar pour un accès direct aux DM.
  - **Premium Iconography** : Remplacement des icônes "+" génériques par des icônes intuitives et colorées (`fas fa-users`, `fas fa-users-cog`, `fas fa-calendar-plus`).
  - **Story Add Button** : Refonte du bouton "Ajouter" avec une icône FontAwesome stylisée.
- **Design System Update** :
  - Mise en place d'un système de design unifié pour les actions de l'en-tête avec des "tokens" de couleur (Bleu pour Amis, Violet pour Groupes, Orange pour Événements).
  - Amélioration du contraste et de la visibilité en mode sombre pour tous les éléments interactifs.

### Fixed
- **Layout & Responsivité** :
  - **Responsive Dropdown** : Correction de l'alignement et du clipping en mode "Laptop" en centrant le menu par rapport à l'en-tête de la sidebar.
  - **Truncation des Pseudos** : Limite de 10 caractères appliquée aux noms d'amis pour préserver l'intégrité du layout.
  - **DM Link Redirection** : Correction de la logique `dm_id` assurant que l'icône DM d'un ami ouvre la bonne conversation.
- **Stabilité Backend** :
  - Résolution de l'erreur `AttributeError` lors de l'accès à `request.user.get_friends()`.
  - Correction de la boucle de messages de chat pour filtrer les messages système.
  - Correction de la redirection lors de l'atteinte du quota de création de groupe.

---

## [2.3.2] - 2026-03-16 ([Unified Admin & Social UI Fixes])

### Added
- **Administration Unifiée (Phase 3)** :
  - Centralisation de la gestion des **Groupes** et **Événements** dans le dashboard d'administration personnalisé.
  - CRUD complet pour les Événements (Modération, Édition, Suppression).
  - **Curated Tags** : Mise en place de badges visuels (GROUP, EVENT) avec codes couleurs dédiés dans les listes administratives.
  - Statistiques en temps réel pour la communauté sur le dashboard principal.

### Fixed
- **Social UI (Otaku Card)** :
  - Correction de l'alignement des icônes DM dans la liste d'amis ; les icônes sont désormais ancrées à l'intérieur des cartes pour un design plus propre.
  - Amélioration des transitions et de l'effet de survol (hover) sur les éléments de la carte Otaku.
- **Navigation Admin** : Sidebar mise à jour avec des liens directs vers les nouvelles sections communautaires.

---

## [2.3.1] - 2026-03-15 ([User Ranks & Event Management])

### Added
- **Système de Rangs (Phase 4)** :
  - Implémentation de 13 rangs (Civil à Shadow Monarch) basés sur le niveau.
  - Nouvelles métadonnées de rang dans le modèle `User` (Titres, Emojis, Couleurs).
  - Affichage dynamique du rang et de l'icône sur le profil utilisateur.
- **Gestion des Événements** :
  - Suppression d'événements désormais possible pour les utilisateurs de Niveau 65+ (Yonko Commander).
  - Interface de suppression avec confirmation sur la page Forum.
- **Curated Admin Social** :
  - Badges distinctifs pour les Groupes et Événements dans l'interface d'administration.
  - Champs de recherche et filtres améliorés pour la section Social.

### Changed
- **Sécurité Événements** : Restriction stricte de la création et suppression d'événements au Niveau 65+ (Yonko Commander) ou au staff.
- **UI Profil** : Refonte de l'identité du profil pour une meilleure visibilité du prestige de l'utilisateur.

---

## [2.3.0] - 2026-03-12 ([Bulk Upload Stability & Security])

### Fixed Bulk Upload Tracking

- **POST-based Polling** : Le suivi de progression utilise désormais des requêtes `POST`. Cela résout les erreurs "URI Too Long" (414) qui survenaient lors de l'upload de dossiers contenant plus de 100 chapitres.
- **CSRF Resilience** : L'endpoint de progression est désormais `csrf_exempt` (lecture seule), évitant les erreurs 403 lors des changements d'IP (mobiles) ou des sessions expirées.
- **Session Graceful Termination** : Ajout d'une gestion propre des sessions expirées (401 JSON). L'interface utilisateur arrête maintenant le suivi proprement avec un message explicatif au lieu de tenter des reconnexions infinies.

### Optimized I/O & Isolation

- **Isolation par `upload_id`** : Chaque dossier importé est traité dans un répertoire temporaire unique, garantissant qu'aucune collision de nom de fichier ne se produise entre différents chapitres ou uploads simultanés.
- **Direct Extraction Pipeline** : Suppression des copies de fichiers redondantes. Le système extrait les pages directement depuis l'archive assemblée sur SSD vers le stockage final, réduisant l'utilisation du cache disque.
- **Celery Task Migration** : La boucle de gestion des extractions a été déplacée vers Celery (`task_bulk_process_chapters`), libérant totalement les threads du serveur web et évitant les "freezes" d'interface pour l'administrateur.

---

## [2.2.0] - 2026-03-07 ([Data Integrity, Conversion & Infrastructure])

*(Note: Ce patch regroupe des fonctionnalités majeures implémentées récemment mais non documentées dans le journal précédent).*

### Added Compliance (Phase 3.5)

- **Mandatory Email Verification** : Intégration de `django-allauth` avec obligation de vérifier l'email avant accès.
- **Legal Registration Consent** : Checkbox obligatoire (`terms_accepted`) ajoutée au processus d'inscription.
- **Dedicated Legal Pages** : Création des pages `/terms/`, `/privacy/` et `/dmca/` accessibles depuis le footer.
- **GDPR Account Deletion** : Route sécurisée de suppression de compte depuis le profil. Les messages sociaux (`social.Message.sender`) passent en `SET_NULL` pour préserver l'historique de la communauté tout en effaçant l'utilisateur.

### Added Moderation & Conversion (Phase 3.6)

- **Reporting System** :
  - Nouveau modèle générique `Report` pour signaler les utilisateurs, commentaires et messages.
  - Modale globale de signalement et tableau de bord de modération intégré à l'admin.
- **Accès Invité Limité** : Restriction à 3 chapitres gratuits par session pour les non-inscrits, suivie d'une redirection automatique vers la page de conversion (`limit_reached.html`).
- **Système d'Avis & Notes** :
  - Nouveau modèle `Review` (1-5 étoiles) avec calcul dynamique de `average_rating`.
  - Interface interactive sur la page de détail (rating input + flux des avis communautaires).

### Fixed Infrastructure & Uploads

- **Résilience des Uploads** : L'extraction de dossiers gère désormais des erreurs réseau avec un *Exponential Backoff* (retries auto) et décompresse un maximum de 5 fichiers en parallèle (Worker Pool) pour saturer la bande passante sans Timeout.
- **Auto-Cleanup Médias** : Ajout de signaux Django `post_delete` purgeant automatiquement les fichiers physiques (images, ZIP) sur le disque dès qu'un Chapitre ou une Page est supprimé via l'admin.
- **Migration R2 vers Local SSD** : Retour stratégique sur un stockage local (Nginx) pour éliminer la latence Cloudflare R2 ; les fichiers temporaires (`.cbz`/`.pdf`) sont désormais auto-purgés immédiatement après extraction pour économiser de l'espace.
- **CSRF Uploads** : Ajout des domaines de production dans `CSRF_TRUSTED_ORIGINS` pour autoriser les requêtes AJAX JS.

---

## [2.1.1] - 2026-03-07 ([Reader & UX Polish])

### Fixed Reader

- **Scroll Restoration** :
  - Correction d'une "race condition" (condition de course) où le `IntersectionObserver` du lazy loading écrasait la position de lecture sauvegardée pendant le chargement initial.
  - La reprise de lecture (auto-scroll) ramène maintenant l'utilisateur exactement à sa page, de manière cohérente.
- **Mobile Horizontal Overflow** :
  - Résolution de l'effet "écran noir" lors du balayage (swipe) gauche/droite sur mobile.
  - Ajout de directives CSS strictes (`touch-action: pan-y`, `max-width: 100vw!important`) pour bloquer le rebond horizontal natif d'iOS/Android (rubber-banding).

### Fixed UX

- **Page "Limit Reached"** :
  - Transformation des textes d'action en véritables boutons clairs (`btn-primary`, `btn-secondary`).
  - Correction du texte (liste d'avantages) qui se superposait mal sur mobile en utilisant un `span` dans la grille flex.
  - Nettoyage du code (suppression des styles en ligne au profit du block `<style>`).
- **Local Media Fallback** :
  - Ajustement de `settings.py` (`MEDIA_URL`) pour prioriser le filesystem local même si des variables cloud (ex: R2) tronquées restent dans le fichier `.env` local.

---

## [2.1.0] - 2026-03-05 ([Upload Bugs & Progress Tracking])

### Fixed Upload

- **Sauvegarde en Arrière-Plan** :
  - Débogage et correction de l'étape "Sauvegarde des informations" lors des uploads de dossiers sur VPS.
  - Processing déplacé entièrement en tâche de fond pour éviter le blocage de la requête HTTP.
- **Suivi de Progression Concurrent** :
  - Correction du monitoring de progression dans l'interface admin pour les uploads simultanés.
  - Résolution des conflits de clé de session lors de multiples uploads en parallèle.
- **Robustesse Générale** :
  - Amélioration de la gestion des erreurs dans le `FileProcessor` pour continuer le traitement malgré les fichiers corrompus.
  - Meilleure fiabilité du système de cache de progression (`cache`/`session`-based).

---

## [2.0.1] - 2026-03-02 ([Forum Layout Bugs])

### Fixed Forum

- **Layout Central** :
  - Correction de l'alignement du bloc central du forum sur desktop et mobile.
  - Résolution des problèmes de `flexbox` dans les media queries causant des débordements latéraux.
- **Responsive Mobile** :
  - Ajustement des breakpoints CSS pour garantir un affichage correct sur écrans < 480px.
  - Correction du z-index de la sidebar forum sur mobile.

---

## [2.0.0] - 2026-02-27 ([Contabo VPS Migration & Infrastructure])

### Added Infrastructure

- **Migration Contabo VPS** :
  - Migration complète de l'application depuis Render vers un VPS Contabo dédié (Ubuntu).
  - Configuration du serveur : Installation de Python, PostgreSQL, Nginx et Gunicorn.
  - Déploiement Django avec Gunicorn en tant que service `systemd` (`gunicorn.service`).
  - Configuration Nginx comme reverse proxy avec gestion des fichiers statiques et médias.
  - Guide de migration documenté dans `docs/references/CONTABO_MIGRATION_GUIDE.md`.
- **Base de Données** :
  - Migration depuis Neon (PostgreSQL cloud) vers une instance PostgreSQL locale sur le VPS.
  - Transfert complet des données et validation d'intégrité post-migration.
- **Upload Management** :
  - Résolution des problèmes d'upload de gros fichiers (> 1 GB) sur le VPS.
  - Configuration Nginx optimisée (`client_max_body_size`, timeouts) pour les uploads longs.

### Changed Settings

- **`config/settings.py`** : Adaptation des paramètres pour l'environnement VPS (chemins, ALLOWED_HOSTS, DB config).
- **`build.sh`** : Script de build/déploiement mis à jour pour automatiser `collectstatic` et les migrations au redémarrage.

---

## [1.9.2] - 2026-02-23 ([Home Page Layout Polish])

### Fixed Home

- **Badges Overlap Mobile** :
  - Correction du chevauchement des badges Statut et Note sur les cartes manga en vue mobile.
  - Les badges sont maintenant empilés verticalement sur les petits écrans.
- **"Voir tout" Text Wrapping** :
  - Correction du retour à la ligne du lien "Voir tout ->" dans les en-têtes de blocs.
  - Application de `white-space: nowrap` pour maintenir le texte sur une ligne à tous les breakpoints.
- **Visual Parity Catalog ↔ Home** :
  - Les cartes manga de la page d'accueil sont maintenant un miroir exact des cartes du catalogue.
  - Harmonisation des badges, de la typographie et du positionnement des éléments.

---

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
