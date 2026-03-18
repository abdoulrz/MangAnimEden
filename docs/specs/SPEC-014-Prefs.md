# **SPEC-014 : Social Preferences & Notifications**

## **1. Méta-données**

* **Titre :** Préférences Sociales et Gestion des Notifications
* **Statut :** Brouillon
* **Priorité :** Moyenne

## **2. Contexte & Intention ("The Why")**

Donner plus de contrôle à l'utilisateur sur sa visibilité et la manière dont il reçoit des interactions, évitant ainsi la surcharge cognitive (spam).

## **3. Description du Produit ("The What")**

### **User Stories**

* [ ] En tant que **User**, je veux activer un mode "Ne pas déranger" (DND) pour masquer mon statut en ligne.
* [ ] En tant que **User**, je veux choisir quels types de notifications je reçois in-app (Aime, Réponses, Amis).

### **Contraintes UI/UX**

* Section dédiée dans la page "Profil / Paramètres".
* Icône DND spécifique (ex: lune) sur le profil.

## **4. Description Technique ("The How")**

### **Modèles de Données (Schema)**

#### `User` (App: `users`)

* `is_dnd_mode`: BooleanField(default=False)
* `notification_prefs`: JSONField (ou boolean fields individuels) : `pref_notif_likes`, `pref_notif_replies`, `pref_notif_friends`.

### **Logic**

* Le `NotificationService` doit vérifier ces préférences avant de créer une notification.

## **5. Critères de Validation (Checklist)**

* [ ] Si le mode DND est activé, l'indicateur en ligne n'apparaît plus (ou apparaît gris).
* [ ] Les notifications désactivées ne sont plus créées en base de données.
