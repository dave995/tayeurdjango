#!/usr/bin/env python
"""
Script pour forcer l'application des migrations
"""

import os
import django
import subprocess
import sys

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tayeur.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def force_migrate():
    """Forcer l'application des migrations"""
    print("=== Force Migration Script ===")
    
    try:
        # Vérifier la connexion DB
        print("1. Testing database connection...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection successful")
        
        # Appliquer les migrations
        print("2. Applying migrations...")
        subprocess.run([
            'python', 'manage.py', 'migrate', '--noinput'
        ], check=True)
        print("✅ Migrations applied successfully")
        
        # Vérifier le statut des migrations
        print("3. Checking migration status...")
        subprocess.run([
            'python', 'manage.py', 'showmigrations'
        ], check=True)
        
        # Créer le superuser
        print("4. Creating superuser...")
        subprocess.run([
            'python', 'manage.py', 'shell', '-c',
            '''
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('Dave', 'dave@tayeur.com', 'passer123')
    print("Superuser created: Dave/passer123")
else:
    print("Superuser already exists")
            '''
        ], check=True)
        
        print("✅ Migration script completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        sys.exit(1)

if __name__ == '__main__':
    force_migrate()
