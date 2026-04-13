# MangaAnimEden 📚

Plateforme de lecture de manga/manhwa avec fonctionnalités de réseau social.

## 🎯 État Actuel: Tracer Bullet Opérationnel

Le projet suit les principes du **03_METHODOLOGY_AND_CHECKLISTS.md** avec une approche "Tracer Bullets" - nous avons construit une tranche fine qui traverse tout le système pour valider la chaîne technique complète.

### ✅ Ce qui fonctionne

- ✅ Django 5.2 configuré avec apps modulaires (users, catalog, reader, core)
- ✅ Modèle User personnalisé avec authentification par email
- ✅ Modèles de données (Series, Chapter, Page, ReadingProgress)
- ✅ Design System (tokens.css avec palette sombre)
- ✅ Lecteur de manga avec lazy loading (IntersectionObserver)
- ✅ Interface admin Django pour gestion de contenu

---

## 🚀 Démarrage Rapide

### 1. Installation

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
.\venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configuration de la base de données

```bash
# Les migrations sont déjà créées, il suffit de les appliquer
python manage.py migrate
```

### 3. Créer un superuser

```bash
python manage.py createsuperuser
# Email: votre@email.com
# Nickname: VotrePseudo
# Password: ********
```

### 4. Lancer le serveur

```bash
python manage.py runserver
```

Le serveur sera accessible sur : **<http://127.0.0.1:8000>**

---

## 📍 URLs Importantes

- **Admin Django**: <http://127.0.0.1:8000/admin>
- **Lecteur Demo (Tracer Bullet)**: <http://127.0.0.1:8000/reader/demo/>

---

## 📖 Tester le Tracer Bullet

1. Connectez-vous à l'admin Django: `/admin`
2. Créez une **Série** (Series)
3. Créez un **Chapitre** (Chapter) lié à cette série
4. Créez une **Page** avec une image uploadée
5. Visitez `/reader/demo/` pour voir votre page s'afficher !

**Note:** Si aucune page n'existe, vous verrez un message expliquant comment ajouter du contenu.

---

## 🏗️ Architecture du Projet

```text
MangaAnimEden/
├── config/                 # Configuration Django
├── users/                  # Gestion utilisateurs (CustomUser)
├── catalog/                # Séries, Chapitres, Pages
├── reader/                 # Lecteur et progression
├── core/                   # Utilitaires partagés
├── static/                 # CSS, JS, Images
│   ├── css/tokens.css      # Design Tokens (Single Source of Truth)
│   └── js/reader.js        # Module MangaReader
├── templates/              # Templates HTML
│   ├── base.html
│   └── reader/demo.html
├── media/                  # Fichiers uploadés (mangas, avatars)
├── docs/                   # Documentation
│   └── specs/              # Spécifications techniques
└── DEBT.md                 # Suivi de la dette technique
```

---

## 📚 Documentation

- **[03_METHODOLOGY_AND_CHECKLISTS](docs/03_METHODOLOGY_AND_CHECKLISTS.md)**: Principes de développement et listes de vérification
- **[02_ARCHITECTURE](docs/02_ARCHITECTURE.md)**: Structure détaillée
- **[SPEC-001](docs/specs/SPEC-001-Tracer-Bullet.md)**: Spécification du Tracer Bullet
- **[DEBT.md](docs/DEBT.md)**: Dette technique

---

## 🎨 Identité & Design System

Le projet suit une esthétique **moderne et immersive** (Dark Mode Only) basée sur le Glassmorphism.

### 🖋️ Typographie (Single Source of Truth)
- **Interface (UI)** : `'Inter', sans-serif` - Utilisée pour toute l'interface utilisateur, la navigation et les contrôles.
- **Contenu & Lecture** : `'Merriweather', serif` - Utilisée pour les textes longs et les descriptions pour un confort de lecture optimal.

Pour plus de détails, consultez le **[DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md)**.

## 🏗️ Philosophie du Projet

---

## 📄 Licence

***(À définir)**

---

***Créé avec ❤️ suivant les principes du Pragmatic Programming**
