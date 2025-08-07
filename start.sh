#!/bin/bash

# Script de démarrage pour Render
# Applique les migrations avant de démarrer le serveur

echo "=== Starting Tayeur Backend ==="

# Attendre que la base de données soit prête
echo "Waiting for database to be ready..."
sleep 5

# Vérifier la connexion à la base de données
echo "Checking database connection..."
python check_db.py

# Appliquer les migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Vérifier que les migrations ont été appliquées
echo "Checking migrations status..."
python manage.py showmigrations

# Créer un superuser si nécessaire (optionnel)
echo "Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('Dave', 'dave@tayeur.com', 'passer123')
    print('Superuser created: Dave/passer123')
else:
    print('Superuser already exists')
"

echo "Starting Gunicorn server..."
gunicorn wsgi:app --bind 0.0.0.0:$PORT
