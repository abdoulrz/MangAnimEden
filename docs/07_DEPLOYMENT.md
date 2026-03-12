# Automatisation du Déploiement (VPS Contabo)

Ce guide explique comment configurer un **Git Hook** sur votre VPS pour que le déploiement se fasse de manière 100% automatique. Avec cette configuration, chaque fois que vous ferez un `git push` depuis votre ordinateur local, le serveur va automatiquement récupérer le code, mettre à jour la base de données, rafraîchir les fichiers statiques (CSS/JS) et redémarrer.

## Pourquoi c'est nécessaire ?

Même si vous exécutez `python manage.py collectstatic`, le navigateur des utilisateurs ne téléchargera pas le nouveau JavaScript (`reader.js`) tant que le numéro de version (`STATIC_VERSION`) n'a pas changé dans les fichiers HTML. Et ce numéro ne change que si **Gunicorn est redémarré** pour lire le nouveau fichier `settings.py`.

L'automatisation règle tout cela d'un seul coup.

---

## 🛠 Configuration pas à pas

### 1. Connectez-vous à votre VPS

```bash
ssh root@62.171.153.213
```

### 2. Créer le script de déploiement

Nous allons supposer que votre projet git se trouve dans `/home/MangaAnimEden`.
Nous allons créer un petit script bash appelé `deploy.sh` à la racine de votre projet ou dans le dossier de l'utilisateur.

```bash
cd /home/MangaAnimEden
nano deploy.sh
```

### 3. Coller le contenu du script

Dans l'éditeur `nano`, collez exactement ce code :

```bash
#!/bin/bash
echo "🚀 Début du déploiement de MangAnimEDen..."

# Aller dans le répertoire du projet
cd /var/www/manganimeden

# 1. Récupérer le nouveau code
echo "📦 Récupération du code..."
git pull origin main

# 2. Activer l'environnement virtuel et installer les nouvelles dépendances
echo "🐍 Mise à jour de l'environnement Python..."
source venv/bin/activate
pip install -r requirements.txt

# 3. Appliquer les migrations de la base de données
echo "🗄️ Application des migrations..."
python manage.py migrate --noinput

# 4. Rassembler les fichiers statiques (CSS, JS, Images)
echo "🎨 Mise à jour des fichiers statiques..."
python manage.py collectstatic --noinput

# 5. Redémarrer Gunicorn pour appliquer le nouveau code Python (ex: settings.py)
echo "🔄 Redémarrage du serveur..."
sudo systemctl restart gunicorn

# (Optionnel) Redémarrer celery si vous l'utilisez pour les tâches de fond
# sudo systemctl restart celery

echo "✅ Déploiement terminé avec succès !"
```

*Pour sauvegarder et quitter nano : Faites `Ctrl+O`, `Entrée`, puis `Ctrl+X`.*

### 4. Rendre le script exécutable

Donnez les droits d'exécution à ce script :

```bash
chmod +x deploy.sh
```

---

## 🚀 Comment l'utiliser (Pour régler le bug actuel)

Puisque le script est prêt, au lieu de taper des commandes compliquées à chaque fois, vous avez juste à exécuter ce script sur votre serveur.

**Tapez ceci dans le terminal de votre VPS maintenant :**

```bash
./deploy.sh
```

### Que va-t-il se passer concernant le bug "Reprendre lecture" ?

1. Le script va faire le `collectstatic`.
2. Il va **redémarrer Gunicorn** (`systemctl restart gunicorn`).
3. Django va relancer `settings.py` et voir que vous avez modifié `STATIC_VERSION = '2.10.13'`.
4. La page HTML demandera au navigateur de télécharger `reader.js?v=2.10.13` (le nouveau fichier !).
5. Votre lecteur commencera à sauvegarder la progression exacte vers l'API.

---

*(Note technique avancée : Si vous souhaitez plus tard que ce script s'exécute **tout seul** juste en faisant `git push` depuis chez vous, vous pouvez configurer ce qu'on appelle un "Git Bare Repository" et un "Post-Receive Hook". Mais avec `./deploy.sh` vous avez déjà réduit le déploiement à une seule commande simple !)*
