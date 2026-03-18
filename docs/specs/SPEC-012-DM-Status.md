# **SPEC-012 : Direct Messages & Online Indicators**

## **1. Méta-données**

*   **Titre :** Système de Messagerie Privée et Indicateurs de Présence
*   **Statut :** Brouillon
*   **Priorité :** Haute

## **2. Contexte & Intention ("The Why")**

Permettre aux utilisateurs de communiquer de manière privée après avoir établi une relation d'amitié. Cela renforce l'aspect communautaire du site en transformant le lecteur passif en membre actif et connecté.

## **3. Description du Produit ("The What")**

### **User Stories**

*   [ ] En tant que **User**, je veux un sidebar unique "DMs & Groupes" pour centraliser mes discussions.
*   [ ] En tant que **User**, je veux que mes conversations (DMs et Groupes) soient triées par activité récente (LIFO).
*   [ ] En tant que **User**, je veux voir quels amis sont en ligne avec un point vert.
*   [ ] En tant que **User**, je veux envoyer un DM à un ami depuis le forum ou son profil.

### **Contraintes UI/UX**

*   Remplacer le titre "Groupes" par "DMs & Groupes".
*   Le sidebar doit mélanger les Groupes dont l'utilisateur est membre et les conversations DM individuelles.
*   Un indicateur de message non-lu doit être visible.
*   On ne peut engager un DM qu'avec un ami accepté.

## **4. Description Technique ("The How")**

### **Modèles de Données (Schema)**

#### `DirectMessage` (App: `social`)

*   `sender`: ForeignKey(User)
*   `recipient`: ForeignKey(User)
*   `content`: TextField
*   `timestamp`: DateTimeField(auto_now_add=True)
*   `is_read`: BooleanField(default=False)

#### `User` (App: `users`)

*   `last_seen`: DateTimeField(null=True, blank=True)

### **Vues / Logic**

*   **Middleware**: Mettre à jour `last_seen` à chaque requête authentifiée.
*   **API Endpoints**:
    *   `GET /social/messages/private/` : Liste les conversations.
    *   `GET /social/messages/private/{user_id}/` : Historique avec un utilisateur.
    *   `POST /social/messages/private/send/` : Envoi d'un message.

### **Dépendances**

*   Utilisation du `NotificationService` existant pour les alertes de nouveaux messages.

## **5. Critères de Validation (Checklist)**

* [ ] Un utilisateur ne peut pas envoyer de DM à un non-ami.
* [ ] Le point vert s'affiche correctement si `last_seen` < 5 minutes.
* [ ] Les messages non-lus sont mis en évidence.
* [ ] Responsive design sur mobile.
