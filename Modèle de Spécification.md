# **Modèle de Spécification (Spec-Driven Development)**

*À copier dans docs/specs/SPEC-00X-Nom-Fonctionnalite.md avant chaque développement.*

*Basé sur "Mastering AI Spec-Writing" pour clarifier l'intention avant l'action.*

## **1\. Méta-données**

* **Titre :** (Ex: Création d'une Communauté Privée)  
* **Statut :** \[Brouillon | En cours | Validé\]  
* **Priorité :** \[Haute | Moyenne | Basse\]

## **2\. Contexte & Intention ("The Why")**

*Pourquoi construisons-nous cela ? Quelle est la valeur pour le lecteur de manga ?*

Ex: Les utilisateurs veulent discuter des "spoilers" du dernier chapitre de *Solo Leveling* sans ruiner l'expérience des autres. Ils ont besoin d'un espace clos.

## **3\. Description du Produit ("The What")**

*À quoi cela ressemble-t-il ? (Référencez les screenshots si possible)*

### **User Stories**

* \[ \] En tant que **User**, je veux créer un groupe nommé.  
* \[ \] En tant que **Admin de groupe**, je veux valider les demandes d'adhésion.  
* \[ \] En tant que **User**, je veux voir les groupes dont je suis membre dans ma sidebar.

### **Contraintes UI/UX (Basées sur le Design System)**

* Utiliser le composant CardGroup pour l'affichage dans le catalogue.  
* L'accès doit être bloqué visuellement (cadenas) si l'utilisateur n'est pas membre.

## **4\. Description Technique ("The How")**

### **Modèles de Données (Schema)**

\# Proposition de structure  
class Community(models.Model):  
    name \= models.CharField(...)  
    is\_private \= models.BooleanField(default=False)  
    members \= models.ManyToManyField(User, through='Membership')

### **Endpoints API / Vues**

* POST /community/create/  
* GET /community/{slug}/

### **Dépendances**

* A-t-on besoin de Websockets ? (Oui pour le chat temps réel).  
* A-t-on besoin de nouvelles permissions Django ?

## **5\. Critères de Validation (Checklist) ("Definition of Done")**

* \[ \] Le code passe le linter (flake8 / eslint).  
* \[ \] Un test unitaire couvre la création de groupe.  
* \[ \] Un test d'intégration vérifie qu'un non-membre ne peut pas voir le contenu privé.  
* \[ \] L'interface est responsive (Mobile first).