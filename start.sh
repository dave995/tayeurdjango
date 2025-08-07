#!/bin/bash

# Script de démarrage pour Render
# Applique les migrations avant de démarrer le serveur

echo "Applying database migrations..."
python manage.py migrate

echo "Starting Gunicorn server..."
gunicorn wsgi:app --bind 0.0.0.0:$PORT
