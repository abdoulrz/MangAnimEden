# Architecture Monétisation & Premium (Phase 5)

Ce document détaille l'architecture du système de paiement, des accès premium, et du portefeuille utilisateur.

## 1. Modèle Économique (Portefeuille & Crédits)
Afin d'isoler l'application de la volatilité des devises et simplifier les remboursements/récompenses, nous adoptons une approche tokenisée : le Portefeuille (`UserWallet`).
* **1 FCFA = 1 Crédit** (et son équivalent dans les autres devises).
* **1000 FCFA = 1000 Crédits = 50 Chapitres Premium**.
* **Coût d'un Chapitre Premium = 20 Crédits**.

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
3. Le montant certifié modifie la transaction en `SUCCESS` et les `credits_awarded` sont injectés dans l'entité `UserWallet` avec un `select_for_update()` pour inhiber les race conditions.

## 4. Règles de Filtrage et Premium
* **Contenu NSFW** : Séries marquées `nsfw=True`. Invisibles à moins que `request.user.age_verified` soit `True`. Peut aussi être couplé à une monétisation "Heavy-Premium".
* **Lecteur et Accès Paywall** : La logique dans `chap_view` vérifie l'existence de `UnlockedChapter(user, chapter)`. S'il est manquant et que les conditions requièrent un achat (`is_premium=True` ou chapitre `> 50`), le système facture `20 Crédits`. Si `wallet.auto_use_credits` est activé, l'achat s'exécute silencieusement, sinon il redirigera vers la page de conversion.
