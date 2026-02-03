# **Architecture et Structure des Fichiers**

Cette structure est conçue pour séparer les préoccupations ("Separation of Concerns") et faciliter l'évolution du projet.

## **Arborescence du Projet**

PROJET\_MANGA/  
├── docs/                        \# DOCS AS CODE  
│   ├── SPEC\_TEMPLATE.md         \# Le modèle de spécification (voir fichier suivant)  
│   ├── DESIGN\_SYSTEM.md         \# Règles CSS, Couleurs, Typos (basé sur vos images)  
│   ├── ARCHITECTURE.md          \# Diagrammes et décisions techniques  
│   └── CHANGELOG.md  
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

* **Models:** Series, Chapter, Page, Tag, Author.  
* **Optimisation:** Indexation forte sur les Tags pour le filtrage rapide.

### **2\. apps/reader**

Le cœur de l'expérience utilisateur.

* **Models:** ReadingProgress (Lien User \<-\> Chapter \+ page number).  
* **Logique:** Préchargement des pages suivantes (Pre-fetching via JS).

### **3\. apps/community**

La couche sociale (basée sur vos demandes).

* **Models:** CommunityGroup (Public/Private/Invite-only), DiscussionThread, Post.  
* **Feature:** Accès basé sur les rôles (Admin de communauté vs Membre).

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
