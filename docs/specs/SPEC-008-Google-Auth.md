# Spécification Technique : Authentification Google (OAuth2)

| Méta-donnée | Détail |
| :--- | :--- |
| **Titre** | Authentification Google (OAuth2) |
| **Auteur** | Assistant |
| **Date** | 07/02/2026 |
| **Statut** | Brouillon |
| **Version** | 1.0.0 |

## 1. Contexte et Objectifs

### 1.1 Contexte

Actuellement, l'application ne propose qu'une authentification par email/mot de passe. Pour simplifier l'inscription et la connexion, nous souhaitons intégrer l'authentification sociale via Google.

### 1.2 Objectifs

- Permettre aux utilisateurs de s'inscrire via leur compte Google.
- Permettre aux utilisateurs existants de se connecter via Google.
- Assurer une intégration visuelle fluide ("Seamless") avec le design actuel.
- Sécuriser le processus via OAuth2.

## 2. Solutions Techniques

### 2.1 Librairie Choisie : `django-allauth`

Nous utiliserons `django-allauth` pour gérer l'ensemble du flux OAuth2. C'est la solution standard de l'industrie pour Django.

### 2.2 Modèles de Données

- Aucun changement majeur sur le modèle `User`.
- `django-allauth` installera ses propres modèles :
  - `SocialAccount`: Lien entre un User et un ID Google.
  - `SocialToken`: (Optionnel) Token d'accès Google (non nécessaire pour simple login).
  - `Site`: Gestion du domaine (nécessaire pour `allauth`).

## 3. Implémentation

### 3.1 Configuration Backend

- **Apps** : Ajouter `allauth`, `allauth.account`, `allauth.socialaccount`, `allauth.socialaccount.providers.google`.
- **Middleware** : Ajouter `allauth.account.middleware.AccountMiddleware`.
- **Authentification** : Ajouter `allauth.account.auth_backends.AuthenticationBackend`.
- **Paramètres** :
  - `SITE_ID = 1`
  - `LOGIN_REDIRECT_URL = 'home'`
  - `ACCOUNT_EMAIL_REQUIRED = True`
  - `SOCIALACCOUNT_QUERY_EMAIL = True`
  - Configuration du provider Google (Client ID / Secret via variables d'environnement ou Django Admin).

### 3.2 Interface Utilisateur (Frontend)

- **Login / Register Pages** :
  - Remplacer les boutons factices "Continuer avec Google" par les vrais boutons d'action.
  - Utiliser le tag `{% provider_login_url 'google' %}`.
  - Cacher les écrans intermédiaires de `allauth` si possible (auto-signup si l'email est valide).

### 3.3 Flux Utilisateur

1. Utilisateur clique sur "Continuer avec Google".
2. Redirection vers Google Consent Screen.
3. Retour sur le site :
    - **Scénario A (Nouveau)** : Création automatique du compte `User` (basé sur email Google) + Login.
    - **Scénario B (Existant)** : Login immédiat.
    - **Scénario C (Email existant mais pas lié)** : Demande de lien ou auto-link (à configurer).

## 4. Sécurité & Risques

- **HTTPS** : OAuth2 requiert HTTPS. En local, nous tolérons HTTP, mais en prod, HTTPS est obligatoire.
- **Secrets** : Les `CLIENT_ID` et `SECRET` ne doivent PAS être commités. Ils seront gérés via les paramètres Django Admin ou des variables d'env.

## 5. Plan de Test

- [ ] Vérifier que le bouton redirige vers Google.
- [ ] Vérifier la création d'un nouvel utilisateur.
- [ ] Vérifier que l'email est correctement récupéré.
- [ ] Vérifier la connexion d'un utilisateur existant.
