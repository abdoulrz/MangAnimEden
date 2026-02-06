# **Spécification : Logique "Trending" (Catalogue Sidebar)**

## **1. Méta-données**

* **Titre :** Implémentation de la Logique de Tendance (Trending Series)
* **Statut :** En cours
* **Priorité :** Moyenne

## **2. Contexte & Intention ("The Why")**

Actuellement, la sidebar du catalogue affiche "Mangas du Moment" avec des données statiques (placeholders). Les utilisateurs doivent voir les séries réellement populaires pour découvrir du contenu pertinent.
Nous voulons mettre en avant les séries les plus consultées ou les mieux notées.

## **3. Description du Produit ("The What")**

### **User Stories**

* [ ] En tant qu'**Utilisateur**, je veux voir une liste de 3 à 5 séries "Trending" dans la barre latérale du catalogue.
* [ ] En tant qu'**Administrateur**, je veux que cette liste se mette à jour automatiquement en fonction de l'activité.

### **Contraintes UI/UX**

* Réutiliser le design existant des "mini-cards" dans la sidebar (`.sidebar-content`, `.trending-item`).
* Afficher : Cover (petite), Titre, et idéalement un indicateur (Note ou Vues).

## **4. Description Technique ("The How")**

### **Modèles de Données**

* Utiliser le champ existant `Series.views_count` (s'il existe) ou `Series.popularity`.
* Si inexistant, ajouter un champ simple `views_count = models.PositiveIntegerField(default=0)`.

### **Logique Backend**

1. **Tracking des Vues** :
    * Dans `CatalogDetailView` (`catalog/views.py`), incrémenter `series.views_count` à chaque chargement de page (avec une protection basique session/cookie pour éviter le spam F5 si nécessaire, ou juste simple incrément pour le MVP).
    * `Series.objects.filter(id=self.object.id).update(views_count=F('views_count') + 1)`

2. **Context Processor ou Mixin** :
    * Puisque cette sidebar apparaît potentiellement sur plusieurs pages (Catalogue, Home...), créer un Context Processor ou un Tag.
    * Pour le moment, c'est surtout sur le Catalogue. Injecter `trending_series` dans le contexte de `CatalogListView`.
    * Query : `Series.objects.order_by('-views_count')[:5]`

### **Frontend**

* Modifier `catalog/list.html` et `home.html` (si présent) pour itérer sur `trending_series`.

## **5. Critères de Validation**

* [ ] Le champ `views_count` s'incrémente lors de la visite d'une page détail.
* [ ] La sidebar affiche les 5 séries avec le plus de vues.
* [ ] L'affichage gère les cas d'égalité ou de 0 vues (fallback sur date de création ?).
