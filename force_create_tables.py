#!/usr/bin/env python
"""
Script pour forcer la création des tables
"""

import os
import sys

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tayeur.settings')

import django
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def force_create_tables():
    """Forcer la création des tables"""
    print("=== Force Create Tables ===")
    
    try:
        # Vérifier la connexion
        print("1. Testing connection...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Connection OK")
        
        # Supprimer les migrations appliquées (si nécessaire)
        print("2. Resetting migrations...")
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM django_migrations WHERE app = 'api'")
            cursor.execute("DELETE FROM django_migrations WHERE app = 'auth'")
            cursor.execute("DELETE FROM django_migrations WHERE app = 'contenttypes'")
            cursor.execute("DELETE FROM django_migrations WHERE app = 'sessions'")
            cursor.execute("DELETE FROM django_migrations WHERE app = 'admin'")
            print("✅ Migrations reset")
        
        # Appliquer les migrations
        print("3. Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations applied!")
        
        # Créer superuser
        print("4. Creating superuser...")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('Dave', 'dave@tayeur.com', 'passer123')
            print("✅ Superuser created: Dave/passer123")
        else:
            print("✅ Superuser already exists")
            
        print("✅ Tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    force_create_tables()
