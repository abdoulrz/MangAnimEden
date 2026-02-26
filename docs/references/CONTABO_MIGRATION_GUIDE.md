# Guide de Migration vers Contabo VPS (Ubuntu/Debian)

Ce guide détaille les étapes exactes pour migrer **MangaAnimEden** depuis l'environnement de développement local (et l'infrastructure Render/Neon) vers votre nouveau **VPS Contabo** (4 Cores, 8GB RAM, 150GB SSD).

## Architecture Cible

1. **Serveur** : VPS Contabo (Système d'exploitation recommandé : Ubuntu 24.04 ou 22.04 LTS).
2. **Application (Backend)** : Django exécuté par Gunicorn (meilleur que Waitress sur Linux).
3. **Proxy Inversé (Web Server)** : Nginx (pour gérer le SSL, servir les fichiers statiques, et rediriger le trafic vers Gunicorn).
4. **Base de Données** : PostgreSQL installé localement sur le VPS (remplace Neon).
5. **Stockage Médias** : Cloudflare R2 (invariable).

---

## Étape 1 : Préparation du Serveur Contabo

Connectez-vous à votre VPS en SSH avec l'IP fournie par Contabo (ex: `ssh root@62.171.153.213`).

### 1.1 Mise à jour et Sécurisation Basique

```bash
# Mettre à jour les paquets
apt update && apt upgrade -y

# Mettre en place un pare-feu (UFW)
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

### 1.2 Installation des Dépendances Système

```bash
# Installer Python, pip, Nginx, PostgreSQL et les outils nécessaires
apt install python3-pip python3-venv nginx postgresql postgresql-contrib libpq-dev curl git -y
```

---

## Étape 2 : Configuration de la Base de Données (PostgreSQL Local)

Nous allons créer une base de données PostgreSQL directement sur le VPS.

```bash
# Se connecter au compte postgres
sudo -u postgres psql

# Dans le prompt psql, exécuter ces commandes :
CREATE DATABASE manganimeden_db;
CREATE USER manga_user WITH PASSWORD 'votre_mot_de_passe_très_sécurisé';

# Optimiser les paramètres de connexion
ALTER ROLE manga_user SET client_encoding TO 'utf8';
ALTER ROLE manga_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE manga_user SET timezone TO 'Europe/Paris';

# Donner les droits à l'utilisateur
GRANT ALL PRIVILEGES ON DATABASE manganimeden_db TO manga_user;

# Quitter psql
\q
```

---

## Étape 3 : Déploiement du Code MangaAnimEden

### 3.1 Création du répertoire et clonage

```bash
# Créer le dossier du projet dans /var/www/
mkdir -p /var/www/manganimeden
cd /var/www/manganimeden

# Cloner le code (via Git ou en le transférant via SCP/SFTP)
# Exemple si vous utilisez Git :
git clone https://github.com/votre_pseudo/manganimeden.git .
```

### 3.2 Environnement Virtuel et Dépendances

```bash
# Créer et activer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les librairies Python
pip install -r requirements.txt
pip install gunicorn psycopg2-binary # Requis pour Linux et PostgreSQL
```

### 3.3 Configuration du fichier `.env`

Créez le fichier `.env` dans le dossier racine :

```bash
nano .env

# Ajouter le contenu suivant (à remplir avec vos vraies clés) :
DEBUG=False
DJANGO_SECRET_KEY=votre_secret_key_complexe
ALLOWED_HOSTS=votre-domaine.com,62.171.153.213
DATABASE_URL=postgres://manga_user:votre_mot_de_passe_très_sécurisé@localhost:5432/manganimeden_db
# Ajouter également vos clés AWS_ACCESS_KEY_ID, GOOGLE_CLIENT_ID, etc.
```

### 3.4 Préparation de Django

```bash
# Appliquer les migrations sur la nouvelle base Postgres
python manage.py migrate

# Collecter les fichiers statiques (CSS, JS) dans 'staticfiles/'
python manage.py collectstatic --noinput

# (Optionnel) Restaurer les données JSON depuis votre dossier db_dumps/
python manage.py loaddata db_dumps/les_vieux_fichiers.json
```

---

## Étape 4 : Configuration de Gunicorn (Serveur d'Application)

Gunicorn gérera votre application Django en arrière-plan.

### 4.1 Créer un service systemd

```bash
nano /etc/systemd/system/gunicorn.service
```

Collez cette configuration :

```ini
[Unit]
Description=gunicorn daemon for MangaAnimEden
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/manganimeden
Environment="PATH=/var/www/manganimeden/venv/bin"
# Timeout élevé (600s) pour autoriser les longs uploads de scans !
ExecStart=/var/www/manganimeden/venv/bin/gunicorn --access-logfile - --workers 3 --timeout 600 --bind unix:/var/www/manganimeden/manganimeden.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 4.2 Activer et lancer Gunicorn

```bash
systemctl start gunicorn
systemctl enable gunicorn
```

---

## Étape 5 : Configuration de Nginx (Proxy Inversé)

Nginx interceptera les requêtes web et les enverra à Gunicorn.

### 5.1 Créer le bloc serveur Nginx

```bash
nano /etc/nginx/sites-available/manganimeden
```

Collez cette configuration :

```nginx
server {
    listen 80;
    server_name votre-domaine.com 62.171.153.213;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    # Servir les fichiers statiques directement (Très rapide)
    location /static/ {
        root /var/www/manganimeden;
    }

    # Rediriger toutes les autres requêtes vers Gunicorn
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/manganimeden/manganimeden.sock;
        
        # Autoriser de très gros uploads (2GB limit)
        client_max_body_size 2000M;
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
    }
}
```

### 5.2 Activer le site Nginx

```bash
# Activer le fichier
ln -s /etc/nginx/sites-available/manganimeden /etc/nginx/sites-enabled

# Tester la configuration
nginx -t

# Redémarrer Nginx
systemctl restart nginx
```

---

## 🚀 C'est prêt

Votre site devrait maintenant être accessible via l'adresse IP de votre VPS (62.171.153.213).

La prochaine étape consistera à lier votre vrai nom de domaine à cette IP (via les DNS de Cloudflare ou de votre registraire) et à activer le HTTPS (gratuit avec Certbot/Let's Encrypt).
