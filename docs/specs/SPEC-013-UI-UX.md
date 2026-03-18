# **SPEC-013 : UI/UX Improvements (Expansion Sociale)**

## **1. Méta-données**

* **Titre :** Améliorations UX : Réponses Long Press, Événements Repliables et Stories Premium  
* **Statut :** Brouillon  
* **Priorité :** Moyenne

## **2. Contexte & Intention ("The Why")**

Améliorer la fluidité et l'esthétique de l'interface sociale pour offrir une expérience "Premium" qui encourage l'interaction.

## **3. Description du Produit ("The What")**

### **User Stories**

* [ ] En tant que **User**, je veux que les DMs utilisent le même système de réponse/interaction que le forum (Long Press).
* [ ] En tant que **User**, je veux que les événements dans le bloc central aient un layout clair et premium.
* [ ] En tant que **User**, je veux un bouton "Ajouter Story" visuellement affiné mais techniquement stable.

### **Contraintes UI/UX**

* **Long Press** : Réutiliser le système existant (`handlePressStart`/`handlePressEnd` dans `forum.html`).
* **Événements** : Améliorer le design du bloc central sans changement structurel majeur. Focus sur la lisibilité.
* **Stories** : Retouche cosmétique prudente du bouton "Ajouter" (CSS simple, pas de refonte complexe).

## **4. Description Technique ("The How")**

### **Frontend Logic (JS)**

* Mise à jour de `forum.html` logic pour le `longPressDuration`.
* CSS transitions pour les blocs d'événements.
* Glassmorphism et gradients CSS pour les composants Stories.

## **5. Critères de Validation (Checklist)**

* [ ] L'appui long fonctionne sur Desktop (mousedown) et Mobile (touchstart).
* [ ] Les événements sont repliés par défaut ou mémorisent leur état.
* [ ] Le bouton Story respecte le Design System (Glassmorphism).
