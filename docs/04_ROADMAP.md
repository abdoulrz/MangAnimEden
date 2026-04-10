# Roadmap de Finalisation du Projet : MangaAnimEden

Ce document trace la route logique pour emmener le projet de son état actuel jusqu'à la mise en production. Il est construit sur la base des documents existants (`DEBT.md`, `DESIGN_SYSTEM.md`, `CHANGELOG.md`) et respecte la méthodologie du `03_METHODOLOGY_AND_CHECKLISTS.md`.

> **⚠️ RÈGLE D'OR (Spec-Driven Development)** :
> Aucune nouvelle fonctionnalité (Stages 1-5) ne doit être codée sans avoir d'abord créé sa spécification dans `docs/specs/` en utilisant `SPEC_TEMPLATE.md`.

---

## ✅ Historique : Phases Complétées

### Phase 1 : Stabilisation et Dette Technique

- [x] **Gestion des Fichiers Statiques** (STATIC_ROOT, collectstatic).
- [x] **Tests Unitaires** (Core, Catalog, Reader, Users).
- [x] **Nettoyage Architecture** (Migration docs/, cleanup root).

### Phase 2 : Features "Core" Partielle

- [x] **Logique Trending** (DailyStat).
- [x] **Stories Web** (Upload 24h, Group-centric).
- [x] **Gamification Base** (Modèle XP, Friendship, Badges).
- [x] **Gestion de Groupes** (Création niveau 50, Modération).
- [x] **Infrastructure** (Migration Contabo VPS, PostgreSQL local).
- [x] **Uploads Robustes** (Chunked Uploads, Celery, OOM Fix).

---

## 🚀 Nouveau Planning : Les 5 Étapes de Finalisation

### Étape 1 : Expansion Sociale & Communauté

*Objectif : Transformer le lecteur passif en membre actif de la communauté.*

- [x] **Direct Messages (DMs)** : Conversations privées basées sur le statut d'ami (Includes Likes & Replies).
- [x] **Indicateur d'État** : Petit point vert sur l'avatar pour les utilisateurs en ligne.
- [x] **Système de Réponse** : UI "Swipe" et "Long Press" pour répondre à un message avec contexte.
- [x] **Gestion d'Événements UX** : Affichage des événements en blocs **curateurs** dans le sidebar unifié.
- [x] **Emoji Picker** : Intégration d'un sélecteur d'émojis dans les DMs et les Groupes.
- [x] **Stories UX** : Design premium normal/hover pour le bouton de création.
- [x] **Sécurité & Accès** : Gestion des accès NSFW et pack d'abonnement (Champs `User` & backend).
- [x] **Forum Navigation Excellence** : Dropdown d'amis et iconographie premium unifiée.

### Étape 2 : Recherche Avancée & Sagesse (Wisdom)

*Objectif : Offrir une navigation fluide et un contenu culturel de haute qualité.*

- [x] **Sagesse Régionale (Sagesse)** : Collection de **100 citations originales** et sérieuses par langue (Français, Anglais, Espagnol). Pas de contenu "cheap".
- [x] **Moteur de Recherche Live** : Interface réactive avec filtres par Genre, Statut et Auteur.
- [x] **Full-Text Search** : Migration vers PostgreSQL SearchVectors pour la performance.
- [x] **Organisation Catalogue** : Regroupement thématique et par genres (Annulé/Non requis).

### Étape 3 : Administration Professionnelle & Intégrité

*Objectif : Garantir la sécurité des données et la puissance des outils de modération.*

- [x] **Infrastructure & Monitoring** : Intégration de Sentry pour la capture en temps réel des Crash 500 en production.
- [ ] **Admin Dash Enhancements** :
  - [x] **Gestion Unifiée de la Communauté** : Interface pour modérer Groupes et Événements avec tags curateurs.
  - [x] Interface de gestion des **Signalements** (Modèle `Report` prêt).
  - [x] Modération des **Avis** (Reviews).
  - [x] Audit Logs filtrables (Modèle `SystemLog` prêt).
  - [x] Métadonnées étendues dans la gestion des séries.
- [x] **Intégrité des Données** : Utilisation de `select_for_update` sur les opérations critiques (XP, Vues) pour éviter les pertes de données lors de clics simultanés.
- [x] **Quotas & Limites** : Limitation de l'espace de stockage par utilisateur/groupe.
- [x] **Système de Notifications In-App** : Notifications sociales et en temps réel opérationnelles.
- [ ] **Dispatcher Email** : Routage centralisé pour les envois d'emails système.

### Étape 4 : Gamification "Prestige" & UX Premium

*Objectif : Récompenser la fidélité et offrir un sentiment de montée en gamme.*

- [x] **Système de Rangs (Rank System)** : Implémenter la hiérarchie officielle :

| Rank | Title | Level | Perks |
|------|-------|-------|-------|
| 1 | Civilian | 1 | Base access |
| 2 | Rookie Pirate | 5 | Unique badge |
| 3 | Grade 4 Sorcerer | 10 | Profile flair color |
| 4 | E-Rank Hunter | 15 | Custom title tag |
| 5 | Supernova | 20 | Early chapter access: +1 day |
| 6 | Grade 3 Sorcerer | 25 | Exclusive badge tier 2 |
| 7 | C-Rank Hunter | 30 | Profile background unlock |
| 8 | Warlord | 40 | Early chapter access: +2 days |
| 9 | Grade 1 Sorcerer | 45 | Exclusive badge tier 3 |
| 10 | S-Rank Hunter | 50 | **Group Moderator** + profile frame |
| 11 | Yonko Commander | 65 | Early chapter access: +3 days + **Event Moderator** unlock |
| 12 | Special Grade | 80 | Exclusive badge tier 4 + profile border |
| 13 | Shadow Monarch | 100 | All perks + **Admin candidate** status |

---

**Notes:**

- At 5 XP/chapter, reaching level 50 requires roughly 550 chapters read — ambitious but achievable for dedicated readers
- Levels 1–50 are the **progression grind**, with steady rank-ups every ~13 chapters on average
- Levels 50–100 are the **prestige climb**, intentionally slower to keep Moderator and top ranks exclusive
- The jump from level 50 to 65 acts as a natural filter — only truly active readers push past Moderator rank
- Shadow Monarch at level 100 is the clean, iconic ceiling — consider pairing it with a **prestige reset** option that adds a "Monarch" prefix and a unique border while restarting the climb

- [x] **Équilibrage XP** : Après le niveau 50, gain réduit à **4 XP / chapitre** (Grind de prestige).
- [ ] **Reset de Prestige** : Option de redémarrage au niveau 100 avec préfixe "Monarch" et bordure unique.
- [ ] **UX Premium** : Animations (Trending, Hovers) débloquées uniquement à partir du **Niveau 50**.
- [x] **Audit Performance** : Vérification finale du Lazy Loading pour économiser les données mobiles.

### Étape 5 : Monétisation (Afrique) & Lancement

*Objectif : Viabilité économique et préparation à la mise en production.*

- [ ] **Monétisation Locale** :
  - [ ] Système : 50 chapitres gratuits, puis **1000 CFA pour 50 chapitres**.
  - [ ] Intégration micro-paiements (Mobile Money).
- [ ] **Publicité & Ads** :
  - [ ] **Ads Vidéo** : Une publicité obligatoire toutes les 10 minutes de lecture.
  - [ ] **UX Publicitaire** : Boutons de fermeture (X) clairs et accessibles.
- [ ] **Abonnement & Accès (Phase 5 Refinement)** :
  - [ ] **Status Otaku Premium** : Rangs et badges exclusifs liés à l'abonnement.
  - [ ] **Accès 18+ (NSFW)** : Gestion sécurisée de l'accès au contenu mature (par abonnement/vérification).
  - [ ] **Carte Otaku Premium** : Design glassmorphic et animations exclusives pour les abonnés.
- [ ] **SEO & Meta** : Descriptions dynamiques et Open Graph pour les réseaux sociaux.
- [ ] **Maintenance Mode** : Splash page activable pendant les mises à jour.
- [ ] **Passation Client** : Transfert des clés API (Google Cloud), Superuser et manuel d'admin.

---

## 🃏 Ideas & Future Concepts

- **Guild/Group Wars** : Compétition hebdo d'XP entre groupes.
- **Reading Rooms** : Chat en direct pendant la lecture d'un chapitre commun.
- **Micro-Dons** : Support direct aux traducteurs via la plateforme.
- **PWA** : Installation sur l'écran d'accueil mobile.
