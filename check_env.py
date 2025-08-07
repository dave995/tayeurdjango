#!/usr/bin/env python
"""
Script pour vérifier les variables d'environnement
"""

import os

def check_environment():
    """Vérifier les variables d'environnement"""
    print("=== Environment Variables Check ===")
    
    # Vérifier DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print(f"✅ DATABASE_URL: {database_url[:50]}...")
    else:
        print("❌ DATABASE_URL not found!")
    
    # Vérifier DJANGO_SETTINGS_MODULE
    settings_module = os.getenv('DJANGO_SETTINGS_MODULE')
    if settings_module:
        print(f"✅ DJANGO_SETTINGS_MODULE: {settings_module}")
    else:
        print("❌ DJANGO_SETTINGS_MODULE not found!")
    
    # Vérifier SECRET_KEY
    secret_key = os.getenv('SECRET_KEY')
    if secret_key:
        print(f"✅ SECRET_KEY: {secret_key[:20]}...")
    else:
        print("❌ SECRET_KEY not found!")
    
    # Vérifier DEBUG
    debug = os.getenv('DEBUG')
    print(f"✅ DEBUG: {debug}")

if __name__ == '__main__':
    check_environment()
