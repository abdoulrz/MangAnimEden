# Guide de Migration MangAnimEden (Render vers VPS Contabo)

## Pourquoi Migrer vers un VPS Contabo ?

Actuellement, l'hébergement gratuit de **Render (Free Tier)** présente de sévères limitations matérielles :

* **Seulement 512 Mo de RAM :** L'extraction de fichiers volumineux (comme des scans PDF de >100 pages) demande le dézippage et la conversion via `Pillow`/`pypdf`. Ces opérations occupent la mémoire serveur. Si la RAM atteint 512 Mo, Render "tue" l'instance (`OOM Killed`), ce qui cause des **erreurs 502 (Bad Gateway)** ou des crashes en arrière-plan.
* **Temps d'exécution limité (Timeout) :** Render coupe les requêtes web qui durent plus de 30 ou 60 secondes.
* **Système de Fichiers Éphémère :** Impossible de stocker de gros fichiers temporaires localement sur le disque sans risquer de les perdre.

**La Solution : Un Serveur Privé Virtuel (VPS).**
Contabo offre des VPS ultra-compétitifs (ex: **VPS 1 à ~5.50€/mois** avec **6 Go de RAM**, 4 cœurs CPU et 400 Go de stockage NVMe). C'est parfait pour gérer de multiples instances Gunicorn, un Redis pour Background Worker (Celery), et héberger massivement des images manga sans aucun souci de RAM.

---

## 🏗️ Architecture Cible sur le Serveur (Docker + Nginx)

Nous allons abandonner *Waitress* (qui est pour Windows) et utiliser **Gunicorn + Nginx + Docker**, car c'est la norme industrielle pour déployer une app Django en production sous Linux.

**Components :**

1. **Nginx :** Serveur frontal (Reverse proxy) et serveur de fichiers statiques/médias (très haute performance).
2. **Gunicorn :** Serveur WSGI pour exécuter le code Python Django.
3. **Neon PostgreSQL :** Base de données principale (Ou un conteneur Postgres local si vous préférez héberger la BDD vous-même pour 0 latence).
4. **Certbot :** Pour les certificats SSL HTTPS gratuits (Let's Encrypt).
5. **Cloudflare R2 (AWS S3) :** Toujours utilisé pour stocker les images extraites si vous voulez économiser l'espace disque du serveur (ou vous pouvez utiliser le disque NVMe local du VPS, 400 Go c'est énorme !).

---

## 🛠️ Étape par Étape : Le Plan de Déploiement

### Phase 1 : Préparation du Serveur VPS

1. **Acheter le VPS :** Prenez le VPS 1 chez Contabo. Choisissez le système d'exploitation **Ubuntu 24.04 LTS (ou 22.04 LTS)**.
2. **Connexion SSH :** Connectez-vous à votre nouveau serveur via un terminal (PuTTY sous Windows ou directement via Powershell `ssh root@VOTRE_IP_CONTABO`).
3. **Sécurité Initiale :**
    * Mettez à jour le serveur : `sudo apt update && sudo apt upgrade -y`
    * Installez un pare-feu (UFW) et autorisez uniquement SSH, HTTP et HTTPS :

        ```bash
        sudo ufw allow OpenSSH
        sudo ufw allow 'Nginx Full'
        sudo ufw enable
        ```

### Phase 2 : Installation des Prérequis Docker

La méthode la plus propre de déployer MangAnimEden est `Docker Compose`.

1. **Installer Docker & Docker Compose :**

    ```bash
    sudo apt install docker.io docker-compose -y
    sudo systemctl enable --now docker
    ```

### Phase 3 : Clonage du Codeback & Variables d'Environnement

1. **Générer une clé SSH** sur le serveur : `ssh-keygen -t ed25519`.
2. Ajoutez cette clé publique dans les **Deploy Keys** de votre dépôt GitHub.
3. **Cloner le code :**

    ```bash
    cd /home
    git clone git@github.com:abdoulrz/MangAnimEden.git
    cd MangAnimEden
    ```

4. **Créer le fichier `.env` de production :**
    * Créez un fichier `.env` sur le serveur contenant toutes les variables Render actuelles :

    ```env
    DEBUG=False
    DJANGO_SECRET_KEY=votre-cle-secrete-ici
    ALLOWED_HOSTS=manganimeden.com,www.manganimeden.com,VOTRE_IP_CONTABO
    DATABASE_URL=votre_url_neon_postgres_ici
    AWS_ACCESS_KEY_ID=votre_r2_key
    AWS_SECRET_ACCESS_KEY=votre_r2_secret
    AWS_STORAGE_BUCKET_NAME=votre_bucket_name
    AWS_S3_ENDPOINT_URL=votre_endpoint_r2
    ```

### Phase 4 : Conteneurisation (Création des Dockerfiles)

*(Cette étape sera faite dans notre code local et pushée sur Git)*

Nous devrons ajouter 2 fichiers au projet :

1. **`Dockerfile`** :

    ```dockerfile
    FROM python:3.11-slim
    
    # Installer pypdf / rarfile requirements (très important sous Linux)
    RUN apt-get update && apt-get install -y unrar gcc libpq-dev
    
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install gunicorn
    RUN pip install -r requirements.txt
    
    COPY . .
    
    # Scripts de démarrage
    CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "--timeout", "120", "config.wsgi:application"]
    ```

2. **`docker-compose.yml`** :
    Ce fichier pilotera le build de l'application.

### Phase 5 : Nom de Domaine et SSL (HTTPS)

1. Allez chez votre fournisseur de nom de domaine (ex: Hostinger, OVH).
2. Changez vos **Enregistrements A** (DNS) pour qu'ils pointent non plus vers Render, mais vers **L'IP de votre VPS Contabo**.
3. Installez `Nginx` et le certificat SSL sur Contabo :

    ```bash
    sudo apt install nginx certbot python3-certbot-nginx
    ```

4. Générez le HTTPS :

    ```bash
    sudo certbot --nginx -d manganimeden.com -d www.manganimeden.com
    ```

### Phase 6 : Lancement

1. Dans le dossier de l'application sur le VPS :

    ```bash
    sudo docker-compose up --build -d
    ```

    *(Ceci va installer les packages, et lancer les 3 workers Gunicorn en arrière-plan)*
2. **Appliquer les Migrations :**

    ```bash
    sudo docker-compose exec web python manage.py migrate
    sudo docker-compose exec web python manage.py createcachetable
    sudo docker-compose exec web python manage.py collectstatic --no-input
    ```

---

## 🚀 Évolutions Positives Attendues Post-Migration

1. **Zéro crash de RAM :** Avec 6 Go de RAM dispo sur le VPS 1 Contabo, un "Gunicorn Worker" peut consommer 800 Mo de RAM le temps d'extraire un PDF de 200 pages sans que personne ne s'en aperçoive.
2. **Workers d'Arrière-plan :** Sur Render, les threads Python en background sont une "bidouille". Sur un VPS, on pourra (plus tard) intégrer un vrai système de files d'attentes **Celery + Redis** (Phase 4), ce qui garantit qu'aucune extraction n'échoue jamais et s'exécute à 100% en parallèle.
3. **Vitesse :** Si vous choisissez de ne plus utiliser R2 car le VPS a 400 Go de NVMe, le chargement des images passera d'un "téléchargement Cloudflare" à un vrai flux local servi par Nginx, ce qui doperait considérablement les temps de chargement pour les lecteurs.
