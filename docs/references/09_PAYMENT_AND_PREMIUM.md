# Architecture Monétisation & Premium (Phase 5)

Ce document détaille l'architecture du système de paiement, des accès premium, et du portefeuille utilisateur.

## 1. Modèle Économique (Portefeuille & Orbes)
Afin d'isoler l'application de la volatilité des devises et renforcer l'identité "Eden", nous utilisons une unité thématique : l'**Orbe** (symbolisé par **◎**).

### La Symbolique des Orbes
Dans le Domaine de MangAnimEden, les Orbes représentent l'énergie mystique nécessaire pour débloquer les fragments de savoir (chapitres premium). 
- **Symbole** : ◎ (Un double cercle rappelant la concentration d'énergie).
- **Rareté** : Les Orbes s'acquièrent via des contributions ou des achats.

### Taux de Conversion
* **1 FCFA = 1 Orbe** (et son équivalent dans les autres devises).
* **1000 FCFA = 1000 Orbes = 50 Chapitres Premium**.
* **Coût d'un Chapitre Premium = 20 Orbes**.

## 2. Abstraction des Passerelles (Factory Pattern)
Le système doit supporter de multiples opérateurs : **FedaPay** pour le FCFA (Mobile Money local), et potentiellement **Stripe/Crypto** pour l'international.
Pour ce faire, le dossier `core/payments/` implémente un design pattern *Factory* :
- `PaymentGateway` : Interface abstraite dictant `create_payment()`, `verify_webhook()`, etc.
- `FedaPayGateway` / `StripeGateway` : Implémentations concrètes.
- `PaymentGatewayFactory.get_gateway('fedapay')` retourne l'instance prête à l'emploi.

## 3. Modèle Sécurisé pour Webhooks
Les agrégateurs de paiement notifient le serveur avec des requêtes POST (Webhooks). 
Afin de prévenir des injections de crédits frauduleuses :
1. Chaque payload entrant est certifié `Webhook-Signature` (HMAC/Clé publique).
2. L'instance `Transaction` (dont l'état était `PENDING`) est récupérée de la BDD.
3. Le montant certifié modifie la transaction en `SUCCESS` et les `orbes_awarded` sont injectés dans l'entité `UserWallet` avec un `select_for_update()` pour inhiber les race conditions.

## 4. Règles de Filtrage et Premium
* **Contenu NSFW** : Séries marquées `nsfw=True`. Invisibles à moins que `request.user.age_verified` soit `True`. Peut aussi être couplé à une monétisation "Heavy-Premium".
* **Lecteur et Accès Paywall** : La logique dans `chap_view` vérifie l'existence de `UnlockedChapter(user, chapter)`. S'il est manquant et que les conditions requièrent un achat (`is_premium=True` ou chapitre `> 50`), le système facture `20 Orbes`. Si `wallet.auto_use_credits` est activé, l'achat s'exécute silencieusement, sinon il redirigera vers la page de conversion.

> **⚠️ NOTE (Bypass Temporaire)** :
> Actuellement, le paywall dans `reader/views.py` contient un bypass hardcodé (`is_chapter_premium = False`) pour ne pas bloquer les lecteurs durant la phase de production où les passerelles de paiement FedaPay/Stripe ne sont pas encore Live. Ce bypass doit impérativement être retiré lors de l'activation officielle des paiements.

## 5. Stratégie Multi-Passerelle (Alternatives & Redondance)

Puisque FedaPay dépend d'exigences légales régionales strictes (IFU/RCCM), le *Factory Pattern* de notre architecture nous permet de "débrancher" ou d'ajouter d'autres passerelles très facilement pour diversifier les revenus.

### 5.1 Option A : Stripe (Cartes Bancaires Internationales)
* **Le Pourquoi (Why)** : Bien que FedaPay traite les cartes bancaires en Afrique, les banques occidentales (Europe/US) ont tendance à bloquer d'office les transactions vers des passerelles ouest-africaines (leurs systèmes anti-fraude sont très durs). Stripe, à l'inverse, est le standard global.
* **Le Comment (How)** : Implémenter la classe abstraite via `StripeGateway` fonctionnant avec les "Stripe Checkout Sessions" (une page hébergée par Stripe où l'utilisateur saisit sa carte). Lors du paiement, Stripe notifie notre webhook local.
* **Le Résultat (What)** : Un taux d'approbation quasi-parfait (100% de succès) pour les lecteurs d'Europe, d'Amérique ou d'Asie. De plus, étant basé en Espagne, le propriétaire peut ouvrir un compte Stripe instantanément, sans friction légale complexe.

### 5.2 Option B : NOWPayments (Cryptomonnaies & Borderless)
* **Le Pourquoi (Why)** : MangAnimEden cible un public geek/otaku, souvent très à l'aise avec la crypto. La crypto garantit des transactions incensurables, privées, et sans blocages bancaires ni frontières, tout en exigeant un KYC (Identity verification) très allégé pour la plateforme.
* **Le Comment (How)** : Via l'implémentation de `NOWPaymentsGateway`. L'API génère à la volée une adresse de dépôt unique pour chaque demande d'achat (ex: BTC, USDT, ETH). Le backend "écoute" via webhook le moment où la transaction est validée sur la blockchain.
* **Le Résultat (What)** : Une monétisation "Cyberpunk" totalement indépendante des banques traditionnelles, idéale en cas de blocages légaux temporaires sur les réseaux fiat (Devises classiques).

## 6. L'Écosystème "Otaku Premium" (Modèle d'Abonnement)

Le système actuel (Portefeuille / Orbes) est un modèle d'Achat "Pay-As-You-Go" très adapté aux petits paniers d'Afrique (Mobile Money), qui coexiste avec le standard de l'industrie du streaming/scanlation : l'Abonnement Récurrent (Monthly Recurring Revenue).

### Pourquoi garder les deux systèmes (Mensuel vs Recharge) ?
Bien que "Payer 1000 FCFA pour Premium" ou "Recharger 1000 Orbes" puissent sembler redondants, ils ciblent deux comportements distincts :
1. **L'Achat à la carte (Sans engagement) :** Un lecteur peut vouloir lire *uniquement* 3 ou 4 chapitres bloqués. Avec un abonnement forcé, il abandonnerait. Avec les Orbes, il recharge le minimum (ex: 1000 FCFA pour 1000 Orbes), dépense 60 Orbes pour ses chapitres (débloqués à vie), et garde le reste de son solde pour le mois suivant.
2. **Le Stockage (Éviter les frais récurrents) :** Payer tous les mois occasionne des frais bancaires et des frictions d'UX. Un lecteur fidèle peut charger 5000 Orbes d'un coup, puis activer l'utilisation automatique pour payer 5 mois de Premium sans ressortir sa carte.
3. **L'Économie In-App (Futur) :** Les Orbes permettront l'ajout de micro-dons (tips aux traducteurs) et d'achats cosmétiques (badges forum, couleurs de profil).

* **Le Comment (How) de l'Otaku Premium** : 
    - Le modèle de données utilisateur possède `is_active_premium` (déduit de `premium_expires_at`).
    - Dans la couche View/Template, on court-circuite le paywall d'achat par Orbes avec une vérification globale (`request.user.is_active_premium`).

* **Les "Perks" (Qu'est-ce qu'ils obtiennent via Premium) :**
    1. **🚫 Zéro Publicité (Ad-Free Experience)** : Disparition totale des publicités vidéos ou bannières (les autres utilisateurs "Civilian" subissent les ads). L'expérience de lecture la plus propre.
    2. **⚡ Fast-Pass (Accès Anticipé)** : Possibilité de lire les derniers chapitres brûlants (Solo Leveling, One Piece, etc.) le jour de la sortie. Les utilisateurs gratuits devront attendre 48h ou 72h.
    3. **👑 Cosmétique Exclusive (Glassmorphism)** : Le passage au statut d'Otaku Premium débloque des UI spécifiques. Leurs DEUX "Cartes de Profil" (Principale et Otaku Card RPG) perdent leur design standard au profit d'un effet *Glassmorphic* (verre poli et translucide) avec des bordures lumineuses (Néons, Dorées), s'adaptant à notre design system. Un badge exclusif "🌟 Otaku Premium" est ajouté.
    4. **💎 Prestige Social** : Leur nom s'affiche avec une couleur unique (dorée/néon) dans les commentaires et le chat DMs, prouvant leur rang et imposant le respect dans la communauté.
