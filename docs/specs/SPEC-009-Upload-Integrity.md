# **SPEC-009-Chunked-Uploads : Robustesse des Gros Transferts**

*Statut : Brouillon | Priorité : Haute*

## **1. Contexte & Intention ("The Why")**

L'upload de contenu (séries complètes) peut représenter plusieurs gigaoctets. Actuellement, ces transferts sont vulnérables aux instabilités réseau et aux timeouts serveur.
L'objectif est d'implémenter un système d'upload par morceaux (chunking) pour :

1. **Fiabilité** : Permettre la reprise en cas de déconnexion.
2. **Performance** : Réduire la charge mémoire du serveur en traitant des petits fragments.
3. **Expérience** : Fournir une progression d'upload précise.

## **2. Description du Produit ("The What")**

### **User Stories**

- [ ] En tant qu'**Uploadeur**, je veux que mes gros fichiers (>1GB) s'uploadent sans erreur, même si ma connexion faiblit.
- [ ] En tant qu'**Admin**, je veux voir une progression temps réel de l'assemblage du fichier.

### **Contraintes UI/UX**

- Barre de progression fluide reflétant l'envoi des morceaux.
- Gestion automatique des tentatives (retry) en cas d'échec d'un morceau.

## **3. Description Technique ("The How")**

### **Mécanisme de Chunking**

- Le client découpe le fichier en morceaux (ex: 5MB).
- Chaque morceau est envoyé avec un `chunk_index`, un `total_chunks` et un `upload_id` unique.
- Le serveur stocke les morceaux dans un répertoire temporaire.
- Une fois le dernier morceau reçu, le serveur assemble le fichier final et le transmet au `FileProcessor`.

### **Endpoints API**

- `POST /administration/upload/chunk/` : Reçoit un fragment.
- `POST /administration/upload/complete/` : Déclenche l'assemblage final.

## **4. Modèles de Données (Schema)**

```python
# catalog/models.py (ou une app dédiée)
class ChunkedUpload(models.Model):
    upload_id = models.UUIDField(default=uuid.uuid4)
    file_name = models.CharField(max_length=255)
    total_chunks = models.IntegerField()
    status = models.CharField(choices=[('uploading', 'En cours'), ('completed', 'Terminé')])
    created_at = models.DateTimeField(auto_now_add=True)
```

## **5. Critères de Validation (Checklist)**

- [ ] Un fichier de 2GB est uploadé avec succès sur un serveur avec 512MB de RAM (preuve de streaming/chunking).
- [ ] La coupure réseau pendant l'upload ne corrompt pas le fichier final après reprise.
- [ ] Les fichiers temporaires sont nettoyés après assemblage.

---
⛩️ **La fiabilité est la priorité.**
