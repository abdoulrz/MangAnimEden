# MangaAnimEden 📚

Plateforme de lecture de manga/manhwa avec fonctionnalités de réseau social.

## 🎯 État Actuel: Tracer Bullet Opérationnel

Le projet suit les principes du **Guide Méthodologique** avec une approche "Tracer Bullets" - nous avons construit une tranche fine qui traverse tout le système pour valider la chaîne technique complète.

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

- **[Guide Méthodologique](Guide%20Méthodologique.md)**: Principes de développement
- **[Architecture Dossiers](Architecture%20Dossiers.md)**: Structure détaillée
- **[SPEC-001](docs/specs/SPEC-001-Tracer-Bullet.md)**: Spécification du Tracer Bullet
- **[Checklists Qualité](Checklists%20Qualité.md)**: Listes de vérification
- **[DEBT.md](DEBT.md)**: Dette technique

---

## 🎨 Philosophie du Projet

Ce projet suit une approche **Spec-Driven** et **DRY** inspirée de:

- *The Pragmatic Programmer* (Tracer Bullets, DRY, Broken Windows)
- *The Checklist Manifesto* (Checklists qualité)
- *Mastering AI Spec-Writing* (Documentation structurée)

**Single Source of Truth:**

- Design Tokens → `static/css/tokens.css`
- Documentation technique → `docs/`
- Dette technique → `DEBT.md`

---

## 🔮 Prochaines Étapes

Voir le fichier de tâches pour la roadmap détaillée. Les prochaines fonctionnalités incluent:

1. Navigation entre pages/chapitres
2. Système d'authentification complet (login/register UI)
3. Catalogue de mangas avec recherche
4. Système de communauté (groupes, discussions)
5. Gamification (XP, niveaux, badges)

---

## 📝 Contribuer

Ce projet suit des checklists strictes avant chaque commit. Voir `Checklists Qualité.md` pour les phases de développement.

---

## 📄 Licence

***(À définir)**

---

***Créé avec ❤️ suivant les principes du Pragmatic Programming**
