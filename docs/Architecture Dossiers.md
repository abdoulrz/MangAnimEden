# **Architecture et Structure des Fichiers**

Cette structure est conçue pour séparer les préoccupations ("Separation of Concerns") et faciliter l'évolution du projet.

## **Arborescence du Projet**

PROJET\_MANGA/  
├── docs/                        \# DOCS AS CODE  
│   ├── Architecture Dossiers.md \# Ce fichier
│   ├── SPEC_TEMPLATE.md         \# Modèle pour nouvelles features (Rename de Modèle de Spéc.)
│   ├── DESIGN_SYSTEM.md         \# Palette, Typography, Composants (Généré depuis CSS)
│   ├── CHANGELOG.md             \# Historique des versions
│   ├── CHECKLIST.md             \# Checklists Qualité.md
│   ├── COMPLEX_IMPLEMENTATION_MEMO.md \# Notes sur features complexes (Admin, Sécurité)
│   ├── PROJECT_COMPLETION_ROADMAP.md  \# Roadmap globale de finalisation
│   ├── DEBT.md                  \# Dette technique
│   ├── TEST_USERS.md            \# Identifiants de test
│   ├── Structure_frontend.js    \# Référence architecture JS
│   └── ...  
│  
├── config/                      \# COEUR DJANGO (ex-project\_name)  
│   ├── settings/  
│   │   ├── base.py              \# Config commune  
│   │   ├── dev.py               \# Config locale (Debug=True)  
│   │   └── prod.py              \# Config prod (Sécurité, S3, CDN)  
│   ├── urls.py  
│   └── wsgi.py  
│  
├── apps/                        \# DOMAINES MÉTIER (Modularité)  
│   ├── core/                    \# Mixins, Utils, Modèles abstraits  
│   ├── users/                   \# Auth, Profils lecteurs, Rôles  
│   ├── catalog/                 \# Mangas, Manhwas, Genres, Auteurs  
│   ├── reader/                  \# Logique d'affichage des images, progression  
│   └── community/               \# Groupes, Discussions, Commentaires privés  
│  
├── static/                      \# ASSETS STATIQUES (Design System)  
│   ├── css/  
│   │   ├── tokens.css           \# Variables : Couleurs, Espacements (Vos screenshots)  
│   │   ├── components/          \# Cards, Buttons, Inputs  
│   │   └── layouts/             \# Grid, Reader view  
│   ├── js/  
│   │   ├── reader.js            \# Logique du lecteur (navigation, zoom)  
│   │   └── community.js         \# Websockets pour le chat  
│   └── img/                     \# Placeholders, Logos  
│  
├── media/                       \# USER GENERATED CONTENT (Uploads)  
│   ├── mangas/                  \# Structure stricte : /slug-manga/chapitre-X/  
│   └── avatars/  
│  
├── templates/                   \# HTML (Django Templates)  
│   ├── base.html                \# Squelette principal  
│   ├── components/              \# Fragments réutilisables (Cards, Nav)  
│   ├── catalog/  
│   ├── reader/  
│   └── community/  
│  
├── manage.py  
├── requirements.txt  
├── .gitignore  
└── CHECKLIST.md                 \# Le Checklist Manifesto actif

## **Détails des Applications Clés (Django Apps)**

### **1\. apps/catalog**

Doit gérer la structure complexe des métadonnées.

* **Models:** Series, Chapter, Page, Tag, Author, Favorite.  
* **Optimisation:** Indexation forte sur les Tags pour le filtrage rapide.

### **2\. apps/reader**

Le cœur de l'expérience utilisateur.

* **Models:** ReadingProgress (Lien User \<-\> Chapter \+ page number).  
* **Logique:** Préchargement des pages suivantes (Pre-fetching via JS).

### **3\. apps/community**

La couche sociale (basée sur vos demandes).

* **Models:** CommunityGroup (Public/Private/Invite-only, avec `owner`), GroupMembership (Gestions des bans), DiscussionThread, Post.  
* **Feature:** Accès basé sur les rôles (Owner du groupe vs Membre vs Banni).

### **4. apps/users (Gamification)**

Système d'engagement utilisateur via XP et Niveaux.

* **Models:** User (Extended avec `level`, `xp`), Badge, UserBadge.
* **Signals:** `users/signals.py` - Django Signal post_save sur ReadingProgress → Attribution automatique de 5 XP + Vérification Badges.
* **Adapter:** `users/adapter.py` - Surcharge de `django-allauth` pour la génération de `nickname` (Google Auth).
* **Logic:** `calculate_level()` (XP // 100 + 1), `add_xp(amount)`, `BadgeService.check_badges()`.
* **Integration:** Reader marque `ReadingProgress.completed=True` → Signal fire → XP+ & Badges.

### **5. apps/administration (Custom Admin)**

Interface métier pour la gestion du contenu et des utilisateurs.

* **Uploads de Dossiers** :
  * **Contournement Formulaire** : Utilisation d'un `<input type="file" webkitdirectory>` manuel dans le template pour supporter l'envoi de dossiers (listes de fichiers), que les `forms.FileField` Django gèrent mal par défaut.
  * **Traitement en Masse** : Service `bulk_create_chapters_from_folder` qui itère sur les fichiers, extrait le numéro de chapitre via Regex, et déclenche le `FileProcessor`.
* **Infrastructure (Windows)** :
  * Utilisation de **Waitress** comme serveur WSGI pour supporter les timeouts longs (20min) et les gros corps de requête (>1GB) nécessaires pour l'upload de séries complètes.

## **Gestion des Assets (CSS/JS)**

Pour respecter le design de vos images (moderne, sombre, propre), utilisez une architecture CSS **ITCSS** (Inverted Triangle CSS) ou **Tailwind** configuré avec vos propres couleurs.

**Exemple de static/css/tokens.css :**

:root {  
    /\* Palette sombre (inspirée manhwa apps) \*/  
    \--color-bg-primary: \#121212;  
    \--color-bg-secondary: \#1E1E1E;  
    \--color-accent: \#FF4500; /\* Couleur d'action \*/  
    \--color-text-main: \#FFFFFF;  
    \--color-text-muted: \#B0B0B0;

    /\* Espacements (Grille de 4px ou 8px) \*/  
    \--space-sm: 8px;  
    \--space-md: 16px;  
    \--space-lg: 32px;  
    \--space-xl: 64px;

    /\* Typographie \*/  
    \--font-reading: 'Merriweather', serif; /\* Pour le texte long \*/  
    \--font-ui: 'Inter', sans-serif;       /\* Pour l'interface \*/  
}  
