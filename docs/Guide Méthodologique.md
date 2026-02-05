# **LE SYSTÈME : Cadre de Développement pour Plateforme Manga/Manhwa**

Ce document définit les règles d'ingénierie logicielle pour le projet, basées sur les principes de *The Pragmatic Programmer*, *The Checklist Manifesto*, et *Mastering AI Spec-Writing*.

## **1\. Philosophie du Projet (The Pragmatic Mindset)**

### **A. "Tracer Bullets" (Balles traçantes) vs Prototypes Jetables**

Pour une web app complexe (Lecture \+ Réseau Social), ne construisez pas des modules isolés.

* **La Règle :** Construisez immédiatement une "tranche fine" qui traverse tout le système.  
* **Application :** Au lieu de parfaire le lecteur de manga *puis* la gestion des utilisateurs, créez un utilisateur capable d'ouvrir une page de manga vide qui charge une image. Cela valide la chaîne Django \-\> Base de données \-\> Frontend \-\> CDN dès le jour 1\.

### **B. DRY (Don't Repeat Yourself) & Single Source of Truth**

* **Code :** Ne dupliquez pas la logique de validation des images entre le modèle Django et le formulaire.  
* **Design :** Vos screenshots montrent une esthétique précise. Les "Design Tokens" (couleurs, espacements, typographie) doivent être définis à UN seul endroit (variables CSS ou config Tailwind) et nulle part ailleurs.  
* **Docs :** La documentation vit *dans* le code (docs/ folder), pas dans des emails ou des Google Docs perdus. C'est le principe "Docs as Code".

### **C. Spec-Driven Development (Piloté par la Spécification)**

* *Inspiré de "Mastering AI Spec-Writing"*  
* On ne code pas sans une "Spec". Une Spec n'est pas un cahier des charges de 100 pages, mais un fichier Markdown structuré qui définit le **Contexte**, l'**Intention** et les **Critères de Réussite** d'une fonctionnalité.  
* Cela permet d'utiliser des Agents IA (comme moi) efficacement pour générer du code précis.

## **2\. Le Système de Design & Assets (Aligné sur vos images)**

Vos images suggèrent une interface immersive, probablement "Dark Mode" par défaut, avec des grilles de couvertures et une hiérarchie visuelle forte.

### **Structure des Assets**

1. **Atomic Design :** Découpez l'interface en :  
   * *Atomes :* Boutons, Inputs, Labels (Design Tokens).  
   * *Molécules :* Carte de Manga (Image \+ Titre \+ Note), Barre de recherche.  
   * *Organismes :* Header, Grille de Catalogue, Lecteur (Reader).  
   * *Templates :* Mise en page de la page "Communauté".  
2. **Optimisation Manga :**  
   * Le poids des images est l'ennemi. Le système doit prévoir le *Lazy Loading* natif et la conversion WebP automatique côté serveur (Django Signals).

## **3\. Architecture Technique (Django \+ JS)**

### **Backend (Django)**

* **Approche Modulaire :** Séparez clairement Community (social) de Reader (contenu). Si le chat plante, la lecture doit continuer à fonctionner (Principe de "Circuit Breaker" dans le *Periodic Table of System Design*).  
* **Système de Cache :** Indispensable. Les pages de mangas ne changent pas souvent. Utilisez Redis pour mettre en cache les réponses des vues de lecture.

### **Frontend (JS \+ HTML/CSS)**

* **Hybride :** Utilisez le templating Django pour le SEO (Catalogue, Home) et JavaScript (ou HTMX/Alpine.js) pour l'interactivité (Lecteur, Chat, Likes). Cela réduit la complexité par rapport à une SPA (Single Page App) complète.

## **4\. Gestion de la Dette Technique (Broken Windows)**

* **Règle :** "Ne vivez pas avec des fenêtres brisées". Si le CSS d'un bouton est décalé, fixez-le ou notez-le dans un fichier DEBT.md. Ne le laissez pas s'accumuler.