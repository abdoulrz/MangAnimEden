# **Spécification : Stories (Upload & Cleanup)**

**Titre :** Finalisation des "Stories" Éphémères
**Statut :** En cours
**Priorité :** Moyenne

## **2. Contexte & Intention ("The Why")**

Les "Stories" (photos éphémères) sont un standard des apps sociales. Elles permettent aux utilisateurs de partager des moments rapides.
**Changement de scope** : La page "News" est supprimée. Les Stories seront intégrées dans la nouvelle page **"Forum"** (anciennement Social/Chat), devenant le hub communautaire central.

## **3. Description du Produit ("The What")**

### **User Stories**

* [ ] En tant que **User**, je veux accéder au "Forum" pour voir les discussions ET les stories.
* [ ] En tant que **User**, je veux poster une image qui s'affichera pendant 24h dans la barre de stories du Forum.
* [ ] En tant que **User**, je veux voir les stories de la communauté dans un carrousel horizontal au dessus du chat.

### **Contraintes UI/UX**

* **Page** : `/forum/` (Replace `/social/` et `/news/`).
* **Upload** : Bouton "+" dans la barre de stories du Forum.
* **Affichage** : Intégration fluide au-dessus des panels de groupes (Chat).

## **4. Description Technique ("The How")**

### **Modèles de Données**

* **Nouveau Modèle** `social.Story` :
  * `user` (ForeignKey)
  * `image` (ImageField)
  * `created_at` (DateTime)
  * `expires_at` (DateTime, default = created_at + 24h)

### **Logique Métier**

* **Cleanup** : Commande `python manage.py cleanup_stories`.

### **Vues & URLs**

* **Refonte** :
  * `core.views.news_view` -> **SUPPRIMER**.
  * `social.views.chat_home` -> Renommer/Aliaser en `forum_home`.
  * URL `/social/` -> `/forum/`.
* **Add Story** :
  * Endpoint POST `/forum/story/add/`.

## **5. Critères de Validation ("Definition of Done")**

* [ ] La page News n'existe plus (404 ou redirect Forum).
* [ ] La page Forum (/forum/) affiche le Chat et la barre de Stories.
* [ ] L'upload de story fonctionne et s'affiche dynamiquement.
* [ ] Les stories expirent après 24h.
