#!/bin/bash

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur si nécessaire (décommenter si besoin)
# python manage.py createsuperuser --noinput

# Désactiver l'environnement virtuel
deactivate 