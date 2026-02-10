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

### 2.4 Retours Utilisateurs & Fixes (URGENT) ✅ (COMPLÉTÉ)

*Corrections immédiates et ajustements UX demandés.*

#### 2.4.1 Nettoyage & Redondance

- [x] **Suppression Page Domaine** : Rediriger `/domaine/` vers `/profile/` (section intégrée). Supprimer le code mort.
- [x] **Profil** : Supprimer le bloc "Paramètres du profil" (doublon ou inutile).
- [x] **Profil Redesign** : Refondre le bloc "Info Utilisateur" (Niveau, Amis) pour un look plus premium.

#### 2.4.2 Navigation & Footer

- [x] **Footer Global** :
  - [x] Lien "Catalogue" -> `/catalogue/`.
  - [x] Lien "Conditions" -> `/about/#conditions`.
  - [x] Remplacer "Contact" par "About" (Fondateurs, Histoire, Objectifs).
- [x] **Page Détail** :
  - [x] Bouton Retour : "Retour à l'accueil" -> "Retour au Catalogue".
  - [x] Tabs : Réparer les boutons Info/Avis qui ne fonctionnent plus.
  - [x] Liste Chapitres : Afficher 10 chapitres max + Scroll infini/Load more dans un container stylisé.

#### 2.4.3 Fonctionnalités "Quick Wins"

- [x] **Forum** : Réparer le bouton "Ajouter une Story".
- [x] **Thème** : Activer la logique du Theme Switcher (bouton existant).

### 2.5 Gamification & Système de Gestion de Groupes

> **Objectif** : Lier la progression de lecture aux rôles utilisateurs et aux permissions de création/modération de groupes.

- [x] **Spec** : Rédiger `docs/specs/SPEC-006-Gamification-Leveling.md`.
  
#### 2.5.1 Système de Niveaux (Leveling & XP)

- [x] **Backend - Logique XP** :
  - [x] **Signal** : Créer un signal (sur lecture de chapitre) pour attribuer de l'XP (+10 XP / chapitre).
  - [x] **Calcul** : Méthode `User.calculate_level()` basée sur l'XP total.
  - [x] **View** : Mettre à jour `profile_view` pour injecter les vraies données (XP actuel, Next Level XP, Barre de progression) au template.
  
- [x] **Backend - Promotion Automatique** :
  - [x] À niveau 50 (500 chapitres) : `User.role_moderator = True` automatiquement.
  - [x] Signal `post_save` sur `User` pour mettre à jour les rôles.

#### 2.5.2 Système Social (Amis)

- [ ] **Backend - Gestion des Amis** :
  - [ ] Modèle `Friendship` (Demandeur, Receveur, Statut: Pending/Accepted).
  - [x] Logique : Envoyer demande, Accepter, Refuser, Retirer.
  - [x] Compteurs : Méthode pour compter les amis actifs.
- [x] **Frontend - UI Sociale** :
  - [x] Profil Public : Bouton "Ajouter en ami" / "Demande envoyée".
  - [x] Profil Privé : Liste des amis et compteur dans la "Glass Card".
  - [x] Nicknames cliquables : Forum/Chat messages link to public profiles.
- [x] **Tests** : Unit tests pour Friendship model (13 tests).

#### 2.5.2.1 Découverte Sociale (Social Discovery) - PARTIAL COMPLETE

*Permettre aux utilisateurs de découvrir d'autres membres facilement.*

- [x] **Page de Recherche d'Utilisateurs** :
  - [x] Barre de recherche par nickname/username.
  - [x] Filtres : Par niveau.
  - [x] Affichage en grille avec avatars et statistiques.
- [x] **Section "Qui lit cette série ?"** :
  - [x] Sur la page détail manga : Liste des 10 lecteurs actifs récents.
  - [x] Link to Public Profile.
- [ ] **Fil d'Activité / Leaderboard** (DEFERRED):
  - [ ] Activité récente : "User X a terminé Série Y".
  - [ ] Classement par XP/Niveau (Top 10).
  - [ ] Classement par chapitres lus cette semaine/mois.

#### 2.5.3 Système de Badges (Achievements) ✅ (COMPLÉTÉ)

- [x] **Backend - Gestion des Badges** :
  - [x] Modèle `Badge` (Nom, Icone, Condition, Slug).
  - [x] Modèle `UserBadge` (son User-Badge avec date d'obtention).
  - [x] Service d'attribution : Vérifier les règles (e.g. "Premier Chapitre", "100 Chapitres") et débloquer.
- [x] **Frontend - UI Badges** :
  - [x] Affichage du compteur de badges dans la "Glass Card".
  - [x] Grille des badges obtenus sur le profil (Timeline Verticale).

#### 2.5.4 Système de Création de Groupes ✅ (COMPLÉTÉ)

- [x] **Backend - Règles de Création** :
  - [x] Exigence : 500 chapitres lus (niveau 50) pour créer un groupe.
  - [x] Limite de groupes : `max_groups = level // 50` (niveau 50 = 1 groupe, niveau 100 = 2 groupes, etc.).
  - [x] Ajouter champ `Group.owner` (ForeignKey vers User).
  - [x] Validation dans `GroupCreateView` : vérifier niveau et quota.

- [x] **Frontend - UI de Création** :
  - [x] Bouton "Créer un Groupe" visible uniquement si niveau ≥ 50.
  - [x] Message informatif si limite atteinte : "Niveau X requis pour créer plus de groupes".

#### 2.5.5 Permissions de Modération de Groupe ✅ (COMPLÉTÉ)

- [x] **Backend - Permissions** :
  - [x] Modèle `GroupMembership` avec champ `is_banned`.
  - [x] Méthode `Group.ban_user(user)` / `unban_user(user)`.
  - [x] Décorateur `@requires_group_moderator` pour vérifier `request.user == group.owner`.

- [x] **Frontend - Actions Modérateur** :
  - [x] Dans l'interface du groupe : bouton "Bannir" visible uniquement pour le propriétaire.
  - [x] Stories : permission de publier réservée au propriétaire du groupe (ou Modérateurs globaux).

#### 2.5.6 Tests & Validation ✅ (COMPLÉTÉ)

- [x] Tests unitaires pour XP et Leveling.
- [x] Tests d'intégration pour le système d'Amis et Badges.
- [x] Tests de validation des quotas de groupes.
- [x] Tests de permissions de modération.

## 🛡️ Phase 3 : Sécurité, Auth & Intégrité

*Basé sur `COMPLEX_IMPLEMENTATION_MEMO.md`. Ne pas négliger cette phase.*

### 3.1 Authentification & Rôles ✅ (COMPLÉTÉ)

- [x] **Google Auth** : Inscription/Connexion via Google (OAuth2). *Note: Implémentation terminée. Validation finale déplacée en 3.7 (attente Google).*
- [x] **Spec** : Rédiger `docs/specs/SPEC-005-Admin-Dashboard.md`.
- [x] **Middleware** : Décorateur `@requires_role`.
- [x] **Audit Logs** : Modèle `SystemLog`.
- [x] **Dashboard** : Page `/admin-panel/` avec Design System.
  - [x] **Gestion Complète** : Permettre aux admins/staff de gérer entièrement le contenu (séries/chapitres) et les utilisateurs (clés/rôles/bans) sans passer par l'interface Django Admin standard.

### 3.2 Notifications & Social ✅ (COMPLÉTÉ)

- [x] **Email System** :
  - [x] **Config** : Backend Console (Dev).
  - [x] **Features** : Welcome Email (Signal), Password Reset (Views + Templates).
- [x] **Système de Notifications** :
  - [x] Backend : Modèle `Notification` (Type: Like, Reply, System).
  - [x] UI : Dropdown (5 dernières) + Page dédiée "Toutes les notifications".
  - [x] Realtime : Toasts (Non-intrusive bubbles).

### 3.3 Gestion des Uploads (Sécurité)

- [ ] **Validateur** : Magic Bytes check pour les images.
- [ ] **Quotas** : Limites de taille par user.
- [ ] **Optimisation Upload** : Implémenter l'upload par morceaux (Chunked Uploads) pour supporter les très gros fichiers (>1GB) de manière fiable, comme Google Drive.

### 3.4 Recherche Avancée

- [ ] **Moteur de Recherche** :
  - [ ] UI : Présentation des résultats (Live search vs Page de résultats).
  - [ ] Backend : Filtres (Genre, Statut, Auteur) et Tri.

### 3.5 Intégrité des Données

- [ ] **Email Verification** :
  - [ ] Configurer `ACCOUNT_EMAIL_VERIFICATION = 'mandatory'` (allauth).
  - [ ] Templates pour "Confirm your email".
- [ ] **Account Deletion (GDPR)** :
  - [ ] UI : Bouton "Supprimer mon compte" (Zone de danger).
  - [ ] Backend : Soft Delete ou Anonymisation (ne pas casser les commentaires/posts).
- [ ] **Legal Consent** :
  - [ ] Checkbox "J'accepte les CGU" à l'inscription.
- [ ] **Reporting System** :
  - [ ] Backend : Modèle `Report` (Target: User/Comment, Reason, Status).
  - [ ] UI : Bouton "Signaler" (Flag icon).
  - [ ] Admin : Vue de modération des signalements.
- [ ] **Pages Légales & Support** :
  - [ ] Templates : `terms.html`, `privacy.html`, `dmca.html`.
  - [ ] Formulaire de Contact : `/contact/` (Envoi email aux admins).
- [ ] **Cascades de Suppression** : Revoir les `on_delete` pour s'assurer que supprimer un User ne casse pas les discussions de groupe (passer en `SET_NULL` ou Soft Delete).

### 3.6 Support Multi-Formats (CBR, CBZ, PDF, EPUB) ✅ (COMPLÉTÉ)

- [x] **Spec** : Rédiger `docs/specs/SPEC-007-Multi-Format-Reader.md`. *(Intégré dans le développement de l'Upload Folder)*
- [x] **Backend** :
  - [x] Support des archives (CBR/CBZ) : Extraction via `zipfile`/`rarfile`. (Implémenté dans `FileProcessor`)
  - [x] Support PDF : Conversion en images via `pdf2image` ou extraction. (Implémenté via `pypdf`)
  - [x] Support EPUB : Parsing via `EbookLib`. (Gestion via extraction Zip)
  - [x] Modèle `Chapter` : Ajouter champ générique `source_file`. (Fait)
- [x] **Frontend** :
  - [x] Reader unifié. (Le `FileProcessor` convertit tout en images standard `Page`, donc le lecteur actuel fonctionne pour tous les formats).
  - [x] Gestion du chargement progressif.

### 3.7 Validation Finale Google Auth ✅ (COMPLÉTÉ)

*Validé avec les credentials développeur du client.*

- [x] **Implémentation** : django-allauth installé, configuré, UI/UX intégré.
- [x] **Credentials** : Obtenir Client ID / Secret valides (Google Cloud Console).
- [x] **Test Final** : Vérifier le flux complet (Connexion -> Redirection -> Création Compte).

---

## 🎨 Phase 4 : UX, Polish et Design System

*Le "Wow Factor" demandé dans le `DESIGN_SYSTEM.md`.*

### 4.1 Unification Visuelle

- [ ] **Refactor** : Remplacer tout hexadécimal hardcodé par `var(--color-...)`.
- [ ] **Animation** : Hover effects (Glassmorphism), Transitions de page.
- [ ] **Feedback** : Tests pour succès/erreur.

### 4.2 Mobile Experience (Prioritaire)

- [ ] **Responsive Check** : Vérification des grilles et tailles de police sur < 400px.
- [ ] **Touch Targets** : Audit des boutons trop petits.
- [ ] **Navigation** : Test du menu sur mobile (Burger ou Bottom Nav).
- [ ] **Mobile Touch** : Feedback visuel au tap (:active), Swipe gestures.

---

## 🏁 Phase 5 : Préparation au Lancement (Release)

*Dernière ligne droite avant la Prod (Checklist "Flight Check").*

### 5.1 SEO & Meta

- [ ] `<meta>` descriptions dynamiques et Open Graph.
- [ ] **Sitemap & Robots.txt** : Génération automatique (`django.contrib.sitemaps`).

### 5.2 Performance & Deploy

- [ ] **Maintenance Mode** : Page statique 503 pour les mises à jour.
- [ ] **Lazy Loading** : Vérification finale.
- [ ] **Images** : Format WebP.
- [ ] **[PRODUCTION REMINDER]** : Remplacer la Console par un vrai SMTP (SendGrid/AWS) dans `settings/prod.py` lors du déploiement.
- [ ] **Serveur Windows (rappel)** : Utiliser la commande Waitress pour gérer les gros uploads (>1GB) : `waitress-serve --port=8000 --channel-timeout=1200 --max-request-body-size=2147483648 config.wsgi:application`

### 5.3 Passation Client (Checklist de Transfert)

*Garantir que le client possède 100% du contrôle et de la responsabilité.*

- [ ] **Google Auth / API Keys** :
  - [ ] Demander au client de créer son propre **Projet Google Cloud**.
  - [ ] Le client génère ses propres **Client ID** et **Client Secret**.
  - [ ] Mettre à jour ces valeurs dans l'Admin Django (`SocialApp`) ou les variables d'env.
- [ ] **Sécurité Application** :
  - [ ] Générer une nouvelle `SECRET_KEY` unique pour la production (ne pas utiliser celle de dev).
  - [ ] S'assurer que `DEBUG = False`.
  - [ ] Configurer `ALLOWED_HOSTS` avec le domaine final du client (ex: `www.manganimeden.com`).
- [ ] **Comptes Administrateurs** :
  - [ ] Créer un **Superuser** pour le client (email/password sécurisé).
  - [ ] Transmettre les accès via un canal sécurisé (ex: gestionnaire de mots de passe, pas par email clair).
  - [ ] (Optionnel) Désactiver ou supprimer les comptes "Développeur" une fois la passation validée.
- [ ] **Email & Notifications** :
  - [ ] Configurer le SMTP (SendGrid, AWS SES, Mailgun) avec le compte du client pour les emails transactionnels (reset password, notifs).
- [ ] **Hébergement & Base de Données** :
  - [ ] Transférer les accès au serveur (SSH Keys) et à la base de données.
  - [ ] Si AWS/Heroku/DigitalOcean : Transférer la facturation ou le compte au client.
- [ ] **Code & Documentation** :
  - [ ] Livrer le code source final (Zip ou Transfert de repo GitHub/GitLab).
  - [ ] Fournir le guide "Gestion des Clés API" et "Manuel d'Administration".
