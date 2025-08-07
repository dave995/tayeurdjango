#!/usr/bin/env python
"""
Script de migration simple et direct
"""

import os
import sys

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tayeur.settings')

import django
django.setup()

from django.core.management import execute_from_command_line

def simple_migrate():
    """Migration simple"""
    print("=== Simple Migration ===")
    
    try:
        # Appliquer toutes les migrations
        print("Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations applied!")
        
        # Créer superuser
        print("Creating superuser...")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('Dave', 'dave@tayeur.com', 'passer123')
            print("✅ Superuser created: Dave/passer123")
        else:
            print("✅ Superuser already exists")
            
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    simple_migrate()
