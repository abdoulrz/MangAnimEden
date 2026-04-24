# Plan d'Implémentation : Option C (Système Anti-Pub et Avantage Premium)

L'objectif de cette fonctionnalité est d'implémenter trois types d'espaces publicitaires qui seront **intégralement désactivés** si l'utilisateur possède l'attribut `is_active_premium == True`.

## 1. Création des Composants Publicitaires
Nous allons centraliser l'UI des publicités pour pouvoir facilement brancher de vraies régies publicitaires (Google AdSense, etc.) plus tard.
* **`templates/components/ad_banner.html`** : Un espace publicitaire statique (ex: format 728x90 ou carré) avec un placeholder "Espace Partenaire".
* **`templates/components/ad_video_modal.html`** : Une modale plein écran qui assombrira le lecteur avec un compteur "Fermer dans 5 secondes..." (X).

## 2. Intégration N°1 : Le Bloc de la Page d'Accueil
* **Fichier ciblé** : `templates/home.html`
* **Action** : Remplacer la section existante `<section class="home-block promo-panel">` par notre composant conditionné.
* **Logique** : Si Premium, ce bloc disparaitra totalement ou laissera place à une bannière de remerciement Premium.

## 3. Intégration N°2 : La Bannière Stratégique (Catalog & Reader)
* **Fichiers ciblés** : `templates/catalog/detail.html` et `templates/reader/chapter.html`
* **Action** : Placer `ad_banner.html` à des points de friction naturels : 
  * Juste en dessous du sommaire des chapitres sur la page de détail d'un manga.
  * À la toute fin d'un chapitre dans le lecteur (avant le bouton "Chapitre Suivant").

## 4. Intégration N°3 : La Pub Récurrente (Chaque 10 minutes)
* **Fichiers ciblés** : `templates/reader/chapter.html` et `static/js/reader.js`
* **Action** :
  1. Injecter la modale `ad_video_modal.html` dans le HTML du lecteur, uniquement si `not request.user.is_active_premium`.
  2. Ajouter un chronomètre dans `reader.js`. 
  3. **Règle de gestion** : Si le lecteur scrolle/bouge la souris (donc est actif), on accumule du temps. À 600,000 millisecondes (10 minutes), on met la lecture en pause, on affiche la Modale de Pub.
  4. L'utilisateur doit attendre 5 secondes pour pouvoir fermer la pub. Le chronomètre repart ensuite de zéro.
