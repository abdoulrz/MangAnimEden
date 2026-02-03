# **Le Checklist Manifesto du Projet**

Ces listes ne sont pas optionnelles. Elles sont votre filet de sécurité pour éviter les erreurs stupides qui coûtent du temps.

## **🟢 PHASE 1 : Avant de Coder (Le "Spec Check")**

*À vérifier avant d'ouvrir votre IDE.*

* \[ \] **Clarté :** Ai-je rempli le TEMPLATE\_SPECIFICATION.md pour cette tâche ?  
* \[ \] **Assets :** Ai-je les icônes/images nécessaires ou dois-je utiliser des placeholders ?  
* \[ \] **Base de données :** Ai-je vérifié si mes changements de modèle vont casser des données existantes ?  
* \[ \] **Dette :** Y a-t-il une "fenêtre brisée" (bug existant) dans ce module que je devrais réparer en passant ?

## **🟡 PHASE 2 : Pendant le Code (Le "Dev Check")**

*À vérifier avant de commiter.*

* \[ \] **DRY :** Ai-je copié-collé du code ? Si oui, refactoriser en fonction ou mixin.  
* \[ \] **Hardcoding :** Ai-je mis des valeurs en dur (ex: URLs, couleurs hexadécimales) au lieu d'utiliser les variables de config ou le CSS ?  
* \[ \] **Sécurité :**  
  * \[ \] Pas de clés API dans le code.  
  * \[ \] Vérification des permissions (ex: @login\_required) sur chaque nouvelle vue.  
  * \[ \] Les inputs utilisateurs sont-ils sanitisés (Django Forms le fait, mais attention au JS) ?  
* \[ \] **Performance :**  
  * \[ \] Mes requêtes SQL sont-elles optimisées ? (Pas de N+1 queries \-\> utiliser select\_related / prefetch\_related).  
  * \[ \] Les images lourdes sont-elles gérées ?

## **🔴 PHASE 3 : Déploiement / Mise en Prod (Le "Flight Check")**

*À vérifier avant de pousser sur le serveur.*

* \[ \] **Migrations :** python manage.py makemigrations et migrate ont-ils été testés en local ?  
* \[ \] **Static Files :** python manage.py collectstatic a-t-il tourné sans erreur ?  
* \[ \] **Variables d'Env :** Les nouvelles variables (ex: clés AWS S3) sont-elles ajoutées dans le .env de production ?  
* \[ \] **Debug Mode :** DEBUG \= False est-il bien actif ?  
* \[ \] **Backup :** Ai-je un backup récent de la DB avant de déployer ?

## **🔵 Checklist Spécifique : Ajout d'un Nouveau Manga**

*Processus éditorial pour le catalogue.*

* \[ \] Le titre est-il correctement orthographié (SEO) ?  
* \[ \] L'auteur et l'artiste sont-ils liés ?  
* \[ \] La couverture respecte-t-elle le ratio (ex: 2:3) pour ne pas briser la grille ?  
* \[ \] Les images du chapitre sont-elles nommées séquentiellement (001.jpg, 002.jpg...) ?  
* \[ \] Le dossier est-il compressé (WebP) ?