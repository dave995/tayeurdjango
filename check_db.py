#!/usr/bin/env python
"""
Script pour vérifier la connexion à la base de données
"""

import os
import django
from django.core.management import execute_from_command_line

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tayeur.settings')
django.setup()

from django.db import connection

def check_database():
    """Vérifier la connexion à la base de données"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Connexion à la base de données réussie")
            return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return False

if __name__ == '__main__':
    check_database()
