# Plan d'Implémentation : Résolution des 5 Blind Spots (Pré-Lancement)

Conformément à la règle **Pragmatic Architect (Plan → Verify → Execute)**, voici le plan d'action technique détaillé, pragmatique et structuré pour adresser les 5 problèmes critiques avant la mise en production.

> [!CAUTION]
> **User Review Required** : Toutes ces modifications touchent à la stabilité et à la performance du site en production. Veuillez valider cet ordre de priorité technique avant que je ne commence l'exécution (Phase 1).

---

## Stratégie d'Exécution

Nous allons diviser le travail en 3 phases, de l'optimisation invisible la plus critique (Backend) jusqu'au polissage visible (Frontend).

## Phase 1 : Core Backend Optimizations (Priorité Absolue)

Ces modifications garantissent que le VPS ne s'effondrera pas sous la charge ou le poids des données.

### 1.1 Élimination des Requêtes N+1 (Base de données)

* **Objectif** : Passer de 60 requêtes SQL par vue à 3 requêtes globales.
* **Fichiers ciblés** :
  * `catalog/views.py` (Vues de la Home et du Catalogue)
  * `users/views.py` (Vue du Profil utilisateur)
* **Implémentation** :
  * **Home/Catalog** : Injecter `prefetch_related('genres', 'reviews')` et `select_related('author')` sur les requêtes `Series.objects.filter()`.
  * **Annotations** : Utiliser `Count('chapters')` via Django ORM au lieu d'appeler `.chapters.count()` dans les templates.
  * **Vérification** : Installer temporairement `django-debug-toolbar` (en local) pour auditer visuellement la chute du nombre de requêtes SQL.

### 1.2 Conversion WebP à la volée (Stockage)

* **Objectif** : Diviser par 3 le poids des archives (CBZ/PDF) extraites sans perdre de qualité visuelle.
* **Fichiers ciblés** :
  * `catalog/services.py` (`FileProcessor`)
  * `requirements.txt` (si Pillow nécessite une mise à jour pour le support complet WebP)
* **Implémentation** :
  * Lors de l'extraction de chaque page d'archive, ouvrir l'image avec `Pillow` (`Image.open(bytes)`).
  * Convertir en RGB (pour éviter les erreurs d'Alpha/Transparency sur les vieux scans PNG/JPEG).
  * Sauvegarder dans le buffer en spécifiant `.save(format='WEBP', quality=85)`.
  * Enregistrer la `Page` Django avec cette nouvelle extension et ce contenu compressé.

---

## Phase 2 : Monitoring et Sécurité de Production

Ces modifications garantissent que toute erreur en production (`DEBUG=False`) est monitorée et gérée de façon Premium.

### 2.1 Intégration Sentry (Crash Reporting)

* **Objectif** : Recevoir un rapport d'erreur technique détaillé dès qu'un utilisateur rencontre un bug.
* **Fichiers ciblés** :
  * `config/settings.py`
  * `requirements.txt` (`sentry-sdk`)
* **Implémentation** :
  * Ajouter la configuration réseau `sentry_sdk.init(dsn=...)` dans `settings.py`.
  * Protéger l'URL DSN avec une nouvelle variable d'environnement `SENTRY_DSN` dans le `.env`.
  * Ajouter un test logique : Sentry ne doit capter les erreurs **que** si `DEBUG=False` pour éviter de polluer ton dashboard Sentry avec les erreurs de developpement.

### 2.2 Pages de Secours Customisées (Erreurs 404 & 500)

* **Objectif** : Cacher la white-page serveur moche; utiliser le Design System actuel pour guider l'utilisateur.
* **Fichiers ciblés** :
  * `config/urls.py` (Définir `handler404` et `handler500`)
  * `templates/404.html` et `templates/500.html`
* **Implémentation** :
  * Construire deux pages simples utilisant `templates/base.html` (Navbar + Footer inclus).
  * **404** : Afficher un message style "*Ce chemin mène au vide.*" + Un gros bouton "Retour au Catalogue".
  * **500** : "*Le flux de mana est perturbé (Erreur Serveur).* L'administrateur a été notifié." (Lié symboliquement à Sentry).

---

## Phase 3 : Rétention Utilisateurs (Frontend UX)

Ceci clôture l'expérience de lecture pour garantir qu'un utilisateur ne rebondisse pas du site (Bounce Rate).

### 3.1 Tunnel de fin de lecture (Reader End-Funnel)

* **Objectif** : Que se passe-t-il au bout du Chapitre ? Le lecteur doit immédiatement être redirigé vers une nouvelle lecture.
* **Fichiers ciblés** :
  * `templates/reader/chap.html`
  * `reader/views.py`
* **Implémentation** :
  * Mettre à jour la vue de lecture pour déterminer le `next_chapter` et le `previous_chapter` de la série.
  * Au bas du lecteur, une fois toutes les pages lazy-loadées :
    * S'il y a un chapitre suivant : Bouton Sticky massif "⬇️ Lire le chapitre #{next_chapter.number}".
    * Si l'utilisateur a fini la série : Afficher une section "Dans le même genre..." générant 3 recommandations aléatoires ou ciblant la catégorie "Trending".

---

## Plan de Validation (Verification Plan)

* [ ] Installer/Démarrer `django-debug-toolbar` localement. Observer < 10 requêtes sur la `/`.
* [ ] Charger un `.cbz` de 20Mo via l'admin. Vérifier que la taille totale sur le disque des pages extraites est inférieure à 8Mo (Format WebP garanti).
* [ ] Passer manuellement en `DEBUG = False`. Essayer de provoquer une 404. La page du Design System doit s'afficher.
* [ ] Finir le chapitre 1 d'un manga : Le lien automatique vers le Chapitre 2 s'affiche. Terminer un manga non terminé : Les "Recommandations" s'affichent.
