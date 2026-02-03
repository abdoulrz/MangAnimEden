# **SPEC-001: Tracer Bullet - Minimum Viable Reader**

## **1. Méta-données**

* **Titre:** Tracer Bullet - Lecteur de Manga Minimal
* **Statut:** En cours
* **Priorité:** Haute
* **Date:** 2026-02-02

---

## **2. Contexte & Intention ("The Why")**

Avant de construire toutes les fonctionnalités de MangaAnimEden (communauté, catalogue complet, gamification), nous devons valider la chaîne technique complète du projet.

**Objectif:** Créer une "balle traçante" qui traverse toute l'architecture :

* Django (Backend) → Base de données → Template System → Frontend JavaScript → Affichage d'images

**Valeur:** Cela nous permet de :

1. Valider que notre stack technique fonctionne end-to-end
2. Identifier les problèmes d'intégration tôt dans le projet
3. Avoir une base fonctionnelle sur laquelle itérer
4. Tester la performance du chargement d'images (critique pour un lecteur de manga)

---

## **3. Description du Produit ("The What")**

### **User Stories**

* [ ] En tant que **User authentifié**, je veux voir une page de manga s'afficher dans mon navigateur
* [ ] En tant que **User**, je veux que l'image se charge de manière optimisée (lazy loading)
* [ ] En tant que **Developer**, je veux valider que le pipeline Django → Frontend fonctionne

### **Scope Minimal (MVP)**

**Ce qui EST inclus:**

* ✅ Un utilisateur unique (créé manuellement via admin)
* ✅ Un manga unique avec UN chapitre et UNE page
* ✅ Une vue Django qui sert cette page
* ✅ Un template HTML minimaliste
* ✅ Le module JavaScript `MangaReader` qui charge l'image
* ✅ Lazy loading avec IntersectionObserver

**Ce qui N'EST PAS inclus (pour plus tard):**

* ❌ Catalogue complet de mangas
* ❌ Système d'authentification UI (on utilise Django admin)
* ❌ Navigation entre pages/chapitres
* ❌ Système de commentaires ou communauté
* ❌ Design system complet

### **Contraintes UI/UX**

* L'image doit être centrée
* Background sombre (#121212) pour confort visuel
* Le MangaReader doit utiliser le module défini dans `Structure_frontend.js`

---

## **4. Description Technique ("The How")**

### **Architecture**

```text
User Request
    ↓
Django URL Router (/reader/manga/demo/)
    ↓
ReaderView (CBV ou FBV)
    ↓
Query Database (Page.objects.get(...))
    ↓
Render Template (reader.html)
    ↓
Frontend: MangaReader.init()
    ↓
IntersectionObserver → Load Image
```

### **Modèles de Données (Schema)**

```python
# apps/users/models.py
class User(AbstractUser):
    email = EmailField(unique=True)
    nickname = CharField(max_length=50)
    # ... (selon Initialisation_django.py)

# apps/catalog/models.py
class Series(models.Model):
    title = CharField(max_length=200)
    slug = SlugField(unique=True)

class Chapter(models.Model):
    series = ForeignKey(Series)
    number = PositiveIntegerField()

class Page(models.Model):
    chapter = ForeignKey(Chapter)
    image = ImageField(upload_to='mangas/%Y/%m/')
    page_number = PositiveIntegerField()
```

### **Endpoints / Vues**

**URL:** `/reader/demo/`

**View:**

```python
# apps/reader/views.py
def demo_reader_view(request):
    """Tracer bullet: Charge une seule page pour validation"""
    # Récupérer la première page disponible
    page = Page.objects.select_related('chapter__series').first()
    
    context = {
        'page': page,
        'total_pages': 1  # Pour l'instant
    }
    return render(request, 'reader/demo.html', context)
```

### **Template**

```html
<!-- templates/reader/demo.html -->
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Tracer Bullet - Reader</title>
    <style>
        body {
            background: #121212;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .manga-page {
            max-width: 100%;
            height: auto;
        }
    </style>
</head>
<body>
    <div id="reader-container">
        <div id="reader-data" data-total="1" hidden></div>
        <img class="manga-page lazy" 
             data-src="{{ page.image.url }}" 
             alt="Page {{ page.page_number }}">
    </div>
    
    <script src="{% static 'js/reader.js' %}"></script>
</body>
</html>
```

### **Frontend JavaScript**

Utiliser le code de `Structure_frontend.js` avec adaptations minimales.

### **Dépendances**

* Django 4.2+ (LTS)
* Pillow (pour ImageField)
* Python 3.10+

---

## **5. Critères de Validation ("Definition of Done")**

### **Checklist Technique**

* [ ] Les migrations ont été créées et appliquées sans erreur
* [ ] Un superuser peut se connecter au Django Admin
* [ ] Un objet Series, Chapter, et Page existe dans la DB
* [ ] L'URL `/reader/demo/` retourne un status 200
* [ ] L'image s'affiche dans le navigateur
* [ ] Le lazy loading fonctionne (vérifiable dans DevTools Network)
* [ ] Le console.log du MangaReader affiche "MangaReader initialisé"

### **Tests Manuels**

1. **Backend Check:**

   ```bash
   python manage.py shell
   >>> from apps.catalog.models import Page
   >>> Page.objects.first()
   # Doit retourner un objet
   ```

2. **Frontend Check:**
   * Ouvrir Chrome DevTools → Network
   * Naviguer vers `/reader/demo/`
   * Vérifier que l'image se charge avec status 200
   * Vérifier dans Console que "MangaReader initialisé" apparaît

3. **Performance Check:**
   * L'image doit se charger en <2s (local)
   * Vérifier dans Lighthouse que l'image utilise lazy loading

---

## **6. Prochaines Étapes (Hors Scope)**

Une fois ce Tracer Bullet validé:

1. Ajouter la navigation entre pages
2. Implémenter le système d'authentification complet
3. Créer le catalogue de mangas
4. Ajouter le Design System complet
5. Implémenter ReadingProgress

---

## **Notes Techniques**

* **Sécurité:** Pas de @login_required pour ce tracer bullet (on teste juste le chargement)
* **Media Files:** Configurer MEDIA_ROOT et MEDIA_URL dans settings/dev.py
* **Static Files:** Pour l'instant, on inclut reader.js directement sans collectstatic
