# **Spécification : Logique "Trending" (Catalogue Sidebar)**

**Titre :** Implémentation de la Logique de Tendance (Trending)
**Statut :** En cours
**Priorité :** Moyenne

## **2. Contexte & Intention ("The Why")**

Actuellement, la sidebar du catalogue affiche des "Tendances" hardcodées (placeholders). Pour améliorer l'engagement et la découverte de contenu, nous devons afficher les séries les plus populaires basées sur les vues réelles des utilisateurs.

## **3. Description du Produit ("The What")**

### **User Stories**

* [ ] En tant que **Lecteur**, je veux voir les mangas les plus consultés dans la sidebar "Tendances".
* [ ] En tant que **Lecteur**, je veux que la liste soit mise à jour dynamiquement en fonction de l'activité.

### **Contraintes UI/UX**

* Afficher le top 5 des séries.
* Conserver le design actuel (Image, Titre, Rang/Compteur).
* Neumorphism : Intégration fluide dans la sidebar existante.

## **4. Description Technique ("The How")**

### **Modèles de Données**

* **Modification** de `catalog.Series` :
  * Ajout du champ `views_count = models.PositiveIntegerField(default=0)`.

### **Logique Métier**

* **Incrémentation** : À chaque visite sur la `SeriesDetailView` (ou équivalent), incrémenter `views_count`. (Simple counter pour l'instant, pas de tracking par période).
* **Requête** : `Series.objects.order_by('-views_count')[:5]`.

### **Vues**

* **Catalog View** (`catalog.views.CatalogListView` ?) : Ajouter `trending_series` au contexte.

## **5. Critères de Validation ("Definition of Done")**

* [ ] Le champ `views_count` existe en base.
* [ ] Visiter une page de manga incrémente le compteur.
* [ ] La sidebar affiche les 5 séries les plus vues.
* [ ] Pas de régression sur l'affichage du catalogue.
