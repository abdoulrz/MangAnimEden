# **SPEC-002: UI Redesign - Purple/Pink Theme**

## **1. Méta-données**

* **Titre:** Redesign complet de l'interface utilisateur
* **Statut:** En cours
* **Priorité:** Haute
* **Date:** 2026-02-02
* **Référence:** Basé sur les images mockup fournies

---

## **2. Contexte & Intention ("The Why")**

L'interface actuelle est fonctionnelle mais ne correspond pas à l'identité visuelle souhaitée. Les mockups fournis montrent une direction claire vers un design moderne de type "manhwa reader" avec:

* Thème très sombre (#0A0A0A)
* Palette purple/pink vibrante
* Navigation claire et moderne
* Empty states bien conçus
* CTAs gradient attractifs

**Objectif:** Transformer l'application pour correspondre exactement aux mockups tout en préservant la structure backend et les principes DRY.

---

## **3. Description du Produit ("The What")**

### **Analyse des Mockups**

#### Image 1 - Page d'Accueil

* Navigation: Logo + Accueil, Catalogue, Chat, News
* Search bar centrale
* Toggle dark mode
* Bouton "Connexion" violet
* Sections: Catégories populaires, Populaires, Dernières mises à jour
* Empty states avec icônes et messages

#### Image 3 - Page de Connexion

* Titre "MangAnimEDen" en purple gradient
* Card centrée avec "Bon retour!"
* Champs Email et Mot de passe avec icônes
* Bouton "Se connecter" violet
* Option "Continuer avec Google"
* Lien "Créer un compte"

#### Images 4-5 - CTA Section

* Grande bannière gradient purple→pink
* Texte "Prêt à commencer votre aventure manga?"
* Deux boutons: "Créer un compte gratuit" + "Explorer le catalogue"
* Footer avec liens

### **User Stories**

* [ ] En tant que **User**, je vois une interface moderne et cohérente sur toutes les pages
* [ ] En tant que **User**, je peux naviguer facilement entre Accueil, Catalogue, Chat, News
* [ ] En tant que **User**, je vois des empty states informatifs quand il n'y a pas de contenu
* [ ] En tant que **User**, je peux me connecter via une interface élégante
* [ ] En tant que **User**, je suis encouragé à créer un compte via des CTAs attractifs

---

## **4. Description Technique ("The How")**

### **Design Tokens (Nouvelle Palette)**

```css
/* Couleurs principales */
--color-bg-primary: #0A0A0A;        /* Très sombre */
--color-bg-secondary: #141414;
--color-bg-elevated: #1A1A1A;
--color-bg-card: #1E1E1E;

/* Purple/Pink Gradient */
--color-purple-primary: #8B5CF6;    /* Purple */
--color-purple-hover: #7C3AED;
--color-pink-primary: #EC4899;      /* Pink */
--gradient-purple-pink: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%);

/* Texte */
--color-text-primary: #FFFFFF;
--color-text-secondary: #A1A1AA;
--color-text-muted: #71717A;
```

### **Composants à Créer**

#### 1. Navbar Component

* Logo + Brand name
* Navigation links (Accueil, Catalogue, Chat, News)
* Search bar
* Dark mode toggle
* Connexion button

#### 2. Empty State Component

* Icône centrale
* Message descriptif
* Lien optionnel

#### 3. Section Header Component

* Emoji/Icône
* Titre
* Lien "Voir tout"

#### 4. CTA Banner

* Gradient background
* Titre
* Description
* Boutons d'action

#### 5. Footer

* Liens (Catalogue, Conditions, Confidentialité, Contact)
* Copyright

### **Structure des Templates**

```text
templates/
├── base.html                    # Navigation + Footer
├── home.html                    # Page d'accueil redessinée
├── auth/
│   ├── login.html              # Page de connexion
│   └── register.html           # Page d'inscription
├── catalog/
│   └── index.html              # Page catalogue
└── components/
    ├── navbar.html
    ├── empty_state.html
    ├── section_header.html
    ├── cta_banner.html
    └── footer.html
```

---

## **5. Critères de Validation ("Definition of Done")**

### **Checklist Visuelle**

* [ ] La palette de couleurs correspond aux mockups (purple/pink)
* [ ] La navigation est identique (logo, menu, search, toggle, connexion)
* [ ] Les empty states utilisent les mêmes icônes et messages
* [ ] La page de connexion est centrée avec le bon style
* [ ] Le CTA banner a le gradient purple→pink
* [ ] Le footer contient tous les liens requis
* [ ] Les hover effects sont fluides et modernes

### **Checklist Technique**

* [ ] Design tokens centralisés dans tokens.css
* [ ] Composants réutilisables (DRY principe)
* [ ] Responsive design pour mobile
* [ ] Pas de hardcoded values
* [ ] Templates utilisent l'héritage Django

### **Checklist Fonctionnelle**

* [ ] Toutes les pages sont accessibles
* [ ] La navigation fonctionne
* [ ] Les liens "Voir tout" sont fonctionnels
* [ ] Les boutons CTA redirigent correctement

---

## **6. Plan d'Implémentation**

### **Étape 1: Design Tokens**

Mise à jour de `static/css/tokens.css` avec la nouvelle palette

### **Étape 2: Composants de Base**

Création des composants réutilisables dans `templates/components/`

### **Étape 3: Navigation**

Intégration de la navbar dans `base.html`

### **Étape 4: Pages Principales**

* Home page redesignée

* Login/Register pages
* Catalogue page

### **Étape 5: Polish**

Animations, transitions, responsive

---

## **7. Notes Techniques**

### Respect de la Méthodologie

* ✅ **DRY**: Composants réutilisables
* ✅ **Single Source of Truth**: Design tokens
* ✅ **Spec-Driven**: Ce document avant le code
* ✅ **Progressive Enhancement**: Graceful degradation

### Assets Requis

* Logo MangAnimEDen (à créer ou utiliser texte stylisé)
* Icônes pour empty states (utiliser Unicode ou SVG)
