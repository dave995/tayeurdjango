#!/usr/bin/env python3
"""
Script de test pour l'authentification
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/"

def test_registration():
    """Test de l'inscription d'un utilisateur"""
    print("=== Test d'inscription ===")
    
    # Données de test
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password_confirmation": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "user_type": "client",
        "phone": "123456789",
        "address": "Test Address"
    }
    
    # Récupérer le token CSRF
    print("1. Récupération du token CSRF...")
    # Essayer plusieurs URLs pour récupérer le token CSRF
    urls_to_try = [
        f"{API_URL}users/",
        f"{API_URL}workshops/",
        f"{API_URL}api-auth/login/",
        f"{BASE_URL}/admin/login/",
    ]
    
    csrf_token = None
    for url in urls_to_try:
        try:
            print(f"   Essai avec: {url}")
            csrf_response = requests.get(url, cookies={})
            csrf_token = csrf_response.cookies.get('csrftoken')
            if csrf_token:
                print(f"   ✅ Token trouvé avec: {url}")
                break
        except Exception as e:
            print(f"   ❌ Erreur avec {url}: {e}")
            continue
    
    if not csrf_token:
        print("❌ Impossible de récupérer le token CSRF")
        return False
    
    print(f"✅ Token CSRF récupéré: {csrf_token[:10]}...")
    
    # Inscription
    print("2. Tentative d'inscription...")
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token,
    }
    
    response = requests.post(
        f"{API_URL}users/",
        json=user_data,
        headers=headers,
        cookies={'csrftoken': csrf_token}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("✅ Inscription réussie!")
        return True
    else:
        print("❌ Échec de l'inscription")
        return False

def test_login():
    """Test de la connexion"""
    print("\n=== Test de connexion ===")
    
    # Récupérer le token CSRF
    print("1. Récupération du token CSRF...")
    csrf_response = requests.get(f"{API_URL}api-auth/login/", cookies={})
    csrf_token = csrf_response.cookies.get('csrftoken')
    
    if not csrf_token:
        print("❌ Impossible de récupérer le token CSRF")
        return False
    
    print(f"✅ Token CSRF récupéré: {csrf_token[:10]}...")
    
    # Connexion
    print("2. Tentative de connexion...")
    login_data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    
    headers = {
        'X-CSRFToken': csrf_token,
    }
    
    response = requests.post(
        f"{API_URL}api-auth/login/",
        data=login_data,
        headers=headers,
        cookies={'csrftoken': csrf_token}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Connexion réussie!")
        return True
    else:
        print("❌ Échec de la connexion")
        return False

def test_me_endpoint():
    """Test de l'endpoint /me/"""
    print("\n=== Test de l'endpoint /me/ ===")
    
    response = requests.get(f"{API_URL}users/me/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    print("🚀 Démarrage des tests d'authentification...\n")
    
    # Test de l'endpoint /me/ avant authentification
    test_me_endpoint()
    
    # Test d'inscription
    if test_registration():
        # Test de connexion
        if test_login():
            # Test de l'endpoint /me/ après authentification
            print("\n=== Test de /me/ après connexion ===")
            response = requests.get(f"{API_URL}users/me/")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    
    print("\n✅ Tests terminés!") 