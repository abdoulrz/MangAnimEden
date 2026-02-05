# SYSTEME DE DESIGN - MangaAnimEden

Ce document est la source unique de vérité pour le design de l'application.
Il est basé sur les fichiers `tokens.css` et `components.css`.

---

## 1. Principes de Design

L'interface adopte une esthétique **moderne et immersive**, inspirée des plateformes de streaming premium et des applications de lecture de manhwa.

* **Thème** : Sombre profond (Dark Mode only) pour réduire la fatigue visuelle.
* **Esthétique** : Mélange de **Glassmorphism** (transparences floutées) et de **Neumorphism** subtil (effets de relief par ombres portées) pour les éléments interactifs.
* **Accent** : Utilisation de dégradés vibrants (Violet vers Rose) pour les actions principales.

---

## 2. Palette de Couleurs

### Fonds (Backgrounds)

* **Primary** : `#0A0A0A` (Noir profond - Body)
* **Secondary** : `#141414` (Gris très sombre - Sections)
* **Card** : `#1E1E1E` (Cartes, Containers)
* **Input** : `#0F0F0F` (Champs de saisie)

### Accents (Brand Gradients)

* **Primary Gradient** : `linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)` (Violet à Rose)
* **Hover Gradient** : `linear-gradient(135deg, #7C3AED 0%, #DB2777 100%)`
* **Purple Primary** : `#8B5CF6`
* **Pink Primary** : `#EC4899`

### Texte

* **Primary** : `#FFFFFF` (Blanc pur)
* **Secondary** : `#A1A1AA` (Gris clair)
* **Muted** : `#71717A` (Gris moyen)

---

## 3. Typographie

### Polices

* **Interface (UI)** : `'Inter', sans-serif` - Propre, moderne, lisible.
* **Lecture (Reading)** : `'Merriweather', serif` - Confortable pour les textes longs.

### Echelle (Scale)

* **XS** : 0.75rem (12px)
* **SM** : 0.875rem (14px)
* **Base** : 1rem (16px)
* **LG** : 1.125rem (18px)
* **XL** : 1.25rem (20px)
* **2XL** : 1.5rem (24px)
* **3XL** : 2rem (32px)

---

## 4. Composants UI (Neumorphism & Glassmorphism)

### Boutons

#### Primaire (Gradient Glow)

Utilisé pour les actions principales (Connexion, Lecture).

* **Background** : Gradient Purple-Pink
* **Shadow** : `0 8px 32px rgba(139, 92, 246, 0.25)` (Lueur colorée)
* **Hover** : `transform: translateY(-2px)` + Ombre intensifiée.

#### Secondaire (Outline/Ghost)

Pour les actions secondaires.

* **Background** : `#1E1E1E` (Card bg)
* **Border** : 1px solid `#27272A`
* **Hover** : Éclaircissement background.

### Cartes (Cards)

Utilisées pour les Mangas, Postes, etc.

* **Background** : `#1E1E1E`
* **Border** : 1px solid `#27272A` (Subtil)
* **Radius** : `12px`
* **Hover** : `transform: translateY(-2px)` + Border Highlight (`#3F3F46`).

### Inputs (Champs)

* **Background** : `#0F0F0F` (Plus sombre que la carte)
* **Border** : 1px solid `#27272A`
* **Focus** : Border violette (`#8B5CF6`) + Glow subtil.

### Navbar (Glassmorphism)

* **Background** : `rgba(20, 20, 20, 0.85)`
* **Blur** : `backdrop-filter: blur(16px)`
* **Border Bottom** : 1px solid `rgba(255, 255, 255, 0.03)`
* **Shadow** : `0 4px 30px rgba(0, 0, 0, 0.5)`

---

## 5. Espacements & Règles

* **Grille** : Système basé sur 8px.
* **Radius** :
  * `6px` (Small)
  * `8px` (Medium - Boutons)
  * `12px` (Large - Cartes)
  * `9999px` (Full - Pills/Badges)

---

## 6. Iconographie

Usage d'emojis pour le prototypage rapide ou d'icônes SVG (Lucide/Heroicons) stylisées en CSS.
Les icônes doivent être alignées verticalement avec le texte (`flex`, `gap: 8px`).
