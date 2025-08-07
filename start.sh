#!/bin/bash

# Script de démarrage pour Render
# Applique les migrations avant de démarrer le serveur

echo "=== Starting Tayeur Backend ==="

# Attendre que la base de données soit prête
echo "Waiting for database to be ready..."
sleep 5

# Vérifier les variables d'environnement
echo "Checking environment variables..."
python check_env.py

# Vérifier la connexion à la base de données
echo "Checking database connection..."
python check_db.py

# Appliquer les migrations avec le script de migration
echo "Running migration script..."
python migrate_db.py

echo "Starting Gunicorn server..."
gunicorn wsgi:app --bind 0.0.0.0:$PORT
