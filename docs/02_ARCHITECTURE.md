# **Architecture et Structure des Fichiers**

Cette structure est conçue pour séparer les préoccupations ("Separation of Concerns") et faciliter l'évolution du projet.

## **Arborescence du Projet**

```text
PROJET_MANGA/  
├── docs/                        # DOCS AS CODE  
│   ├── 00_SPEC.md               # Vision & Pre-requisites
│   ├── 01_RULES.md              # Pragmatic Architect rules & AI constraints
│   ├── 02_ARCHITECTURE.md       # Ce fichier
│   ├── 03_METHODOLOGY_AND_CHECKLISTS.md # Méthodologie et Checklists Qualité
│   ├── 04_ROADMAP.md            # Roadmap globale de finalisation
│   ├── CHANGELOG.md             # Historique des versions
│   ├── COMPLEX_IMPLEMENTATION_MEMO.md # Notes sur features complexes (Admin, Sécurité)
│   ├── DEBT.md                  # Dette technique
│   ├── DESIGN_SYSTEM.md         # Palette, Typography, Composants
│   ├── SPEC_TEMPLATE.md         # Modèle pour nouvelles features
│   └── references/              # Mémos techniques (Contabo, Frontend, DB)
│  
├── config/                      # COEUR DJANGO 
│   ├── settings/  
│   │   ├── base.py              # Config commune  
│   │   ├── dev.py               # Config locale (Debug=True)  
│   │   └── prod.py              # Config prod (Sécurité, S3, CDN)  
│   ├── urls.py  
│   └── wsgi.py  
│  
├── Django Apps (Racine)/        # DOMAINES MÉTIER (Modularité)  
│   ├── administration/          # Custom Admin métier
│   ├── catalog/                 # Mangas, Manhwas, Genres, Auteurs  
│   ├── core/                    # Mixins, Utils, Modèles abstraits  
│   ├── reader/                  # Logique d'affichage des images, progression  
│   ├── social/                  # Réseau social, Notifications, Discussions
│   └── users/                   # Auth, Profils lecteurs, Rôles, Gamification
│  
├── media/                       # USER GENERATED CONTENT (Uploads locaux)  
│   ├── avatars/                 # Photos de profil
│   ├── Background/              # Bannières de profil
│   ├── badges/                  # Icônes des succès/badges
│   ├── covers/                  # Couvertures des mangas
│   ├── group_icons/             # Icônes des groupes communautaires
│   ├── scans/                   # Pages de mangas extraites (.jpg, .webp)
│   ├── stories/                 # Contenu éphémère (24h)
│   └── manga_temp_uploads/      # Fichiers archives isolés par upload_id
│  
├── static/                      # ASSETS STATIQUES (Design System)  
│   ├── css/  
│   │   ├── tokens.css           # Variables : Couleurs, Espacements
│   │   ├── pages.css            # Styles mutualisés et globaux
│   │   ├── profile.css, etc...  # Styles spécifiques par vue
│   │   └── components/          # Composants UI isolés  
│   ├── js/  
│   │   ├── app.js               # Logique globale, UIKit (Wisdom, Animations)
│   │   └── reader.js            # Logique spécifique du lecteur de Manga  
│   └── img/                     # Placeholders, Logos  
│  
├── templates/                   # HTML (Django Templates)  
│   ├── base.html                # Squelette principal  
│   ├── components/              # Fragments réutilisables (Nav, Header)  
│   └── ... (Par Django App)
│
├── db_dumps/                    # Sauvegardes et fixtures JSON de base de données
├── scripts/                     # Scripts utilitaires Python (DB sync, Migration)
├── tools/                       # Outils de développement externes
├── staticfiles/                 # Généré par Django collectstatic
├── manage.py  
├── requirements.txt  
└── .gitignore  
```

## **Détails des Applications Clés (Django Apps)**

Les applications Django sont situées à **la racine** du projet.

### **1. catalog**

Doit gérer la structure complexe des métadonnées.

* **Models:** Series, Chapter, Page, Tag, Author, Favorite.  
* **Optimisation:** Indexation forte sur les Tags pour le filtrage rapide.

### **2. reader**

Le cœur de l'expérience utilisateur de lecture.

* **Models:** ReadingProgress (Lien User <-> Chapter + page number).  
* **Logique:** Préchargement des pages suivantes (Pre-fetching via JS, `reader.js`).

### **3. social (ex-community)**

La couche communautaire et d'interactions ("Forum").

* **Models:** CommunityGroup (Public/Private/Invite-only, avec `owner`), GroupMembership (Gestions des bans), DiscussionThread, Post, Notification, Report.  
* **Feature:** Accès basé sur les rôles (Owner du groupe vs Membre vs Banni), Timeline temps réel.

### **4. users (Gamification)**

Système d'engagement utilisateur via XP, Niveaux, et Profils Personnalisés.

* **Models:** User (Extended avec `level`, `xp`), Badge, UserBadge, Friendship.
* **Signals:** `users/signals.py` - Django Signal post_save sur ReadingProgress → Attribution automatique d'XP + Vérification Badges + Promotion automatique au rang Modérateur niveau 50.
* **Adapter:** `users/adapter.py` - Surcharge de `django-allauth` pour la génération de `nickname` (Google Auth).
* **Logic:** `calculate_level()` (XP // 100 + 1), `add_xp(amount)`, `BadgeService.check_badges()`.
* **Integration:** Reader marque `ReadingProgress.completed=True` → Signal fire → XP+ & Badges cumulés.

### **5. administration (Custom Admin)**

Interface métier dédiée pour la gestion fluide du contenu (Séries, Uploads de Chapitres) et des modérations utilisateurs sans utiliser le design brutal du Django Admin standard.

* **Uploads de Dossiers** :
  * **Contournement Formulaire** : Utilisation d'un `<input type="file" webkitdirectory>` manuel dans le template pour supporter l'envoi de dossiers entiers.
  * **Asynchronisme (Celery)** : Utilisation de workers Celery (`task_bulk_process_chapters`) pour gérer l'extraction lourde en arrière-plan, évitant tout blocage du serveur web.
  * **Isolation & Sécurité** : Chaque upload est isolé dans un sous-répertoire `<upload_id>/` pour éviter les collisions de noms de fichiers.
  * **Suivi de Progression Robuste** : Polling via `POST` (supporte des centaines d'IDs) et `csrf_exempt` pour une résilience maximale aux déconnexions/timeouts.
  * **Traitement en Masse** : Service `FileProcessor` qui itère sur les fichiers, gère l'extraction des archives (`.cbz`, `.zip`), convertit les PDFs et extrait le numéro de chapitre.
* **Feature:** Interface utilisateur repensée en Neumorphism/Glassmorphism.

## **Gestion des Assets (CSS/JS)**

Pour respecter le design (moderne, sombre, épuré premium), nous utilisons une architecture CSS **Vanilla modulaire** (proche de ITCSS).

**Exemple de `static/css/tokens.css` :**

```css
:root {  
    /* Palette sombre (inspirée manhwa apps) */  
    --color-bg-primary: #121212;  
    --color-bg-secondary: #1E1E1E;  
    --color-accent: #FF4500; /* Couleur d'action */  
    --color-text-main: #FFFFFF;  
    --color-text-muted: #B0B0B0;

    /* Espacements (Grille de 4px ou 8px) */  
    --space-sm: 8px;  
    --space-md: 16px;  
    --space-lg: 32px;  
    --space-xl: 64px;

    /* Typographie */  
    --font-reading: 'Merriweather', serif; /* Pour le texte long */  
    --font-ui: 'Inter', sans-serif;       /* Pour l'interface */  
}  
```

---

## **Mémos de Mise en Œuvre (Complexité)**

*Consolidation technique pour garantir l'intégrité et la sécurité.*

### 1. Administration & Rôles

* **Hiérarchie** :
  * **Superuser** : Accès complet Django Admin. Gère les clés et promeut les admins.
  * **Site Administrator** : Accès Dashboard métier (`/admin-panel/`). Gère les membres et le contenu.
  * **Moderator** : Accès outils frontend (modération chat/forum).
* **Audit Logs** : Chaque action sensible (ban, suppression, promotion) doit être loggée via le décorateur `log_admin_action` dans `SystemLog`.

### 2. Intégrité des Données

* **Cascades de suppression** : Prioriser `SET_NULL` pour les messages et interactions sociales afin de préserver l'historique communautaire lors de la suppression d'un compte (RGPD).
* **Concurrency** : Utiliser `transaction.atomic` pour les calculs d'XP et les transactions de badges afin d'éviter les "Race Conditions".

### 3. Sécurité & Abus

* **Background Processes** : Utiliser impérativement des requêtes `POST` et le décorateur `@csrf_exempt` pour le polling de progression (cf. `UploadProgressStatusView`).
* **Signalements (Report)** : Système générique via `GenericForeignKey` permettant de signaler n'importe quel objet (User, Comment, Message).
