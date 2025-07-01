from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import openai
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import os
import requests

# Configuration OpenAI
openai.api_key = settings.OPENAI_API_KEY

# Configuration pour utiliser la version gratuite
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Modèle gratuit (GPT-3.5-turbo) au lieu de GPT-4
DEFAULT_MODEL = "gpt-3.5-turbo"

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_models_from_fabric(request):
    """
    Génère des modèles de vêtements à partir d'un tissu en utilisant ChatGPT
    """
    try:
        fabric_data = request.data
        
        # Construction du prompt pour ChatGPT
        prompt = f"""Tu es un expert en mode et design de vêtements. Génère 4 modèles de vêtements différents qui seraient parfaits pour ce tissu :

Nom du tissu: {fabric_data.get('name', 'Tissu')}
Description: {fabric_data.get('description', 'Non spécifiée')}
Couleur: {fabric_data.get('color', 'Non spécifiée')}
Prix au mètre: {fabric_data.get('unit_price', 0)}€
Unité: {fabric_data.get('unit_display', 'm')}

Crée des modèles variés qui mettent en valeur les caractéristiques de ce tissu. 
Adapte les styles, les prix et les délais selon le type et la qualité du tissu.

Pour chaque modèle, fournis :
- Un nom créatif et descriptif
- Une description détaillée
- La catégorie (shirt, dress, suit, pants, skirt, other)
- 3-4 styles/tags
- Un prix estimé en euros
- Un délai de confection en jours
- Des notes de design
- L'utilisation du tissu
- Un prompt pour générer une image

Réponds uniquement en JSON valide avec cette structure :
{{
  "models": [
    {{
      "name": "Nom du modèle",
      "description": "Description détaillée",
      "category": "shirt",
      "styles": ["style1", "style2", "style3"],
      "estimatedPrice": 150,
      "estimatedTime": 7,
      "designNotes": "Notes de design",
      "fabricUsage": "Comment utiliser le tissu",
      "imagePrompt": "Prompt pour générer l'image"
    }}
  ]
}}"""

        # Appel à ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en mode et design de vêtements. Tu dois générer 4 modèles de vêtements différents qui seraient parfaits pour le tissu décrit. Réponds uniquement en JSON valide."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=2000
        )

        # Extraction de la réponse
        content = response.choices[0].message.content
        parsed_response = json.loads(content)
        
        return Response({
            'success': True,
            'models': parsed_response.get('models', []),
            'fabric_id': fabric_data.get('id'),
            'fabric_name': fabric_data.get('name')
        })

    except json.JSONDecodeError as e:
        return Response({
            'success': False,
            'error': 'Erreur de parsing de la réponse ChatGPT',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': 'Erreur lors de la génération',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_fabric(request):
    """
    Analyse un tissu avec ChatGPT pour donner des conseils
    """
    try:
        fabric_data = request.data
        
        prompt = f"""Tu es un expert en textiles. Analyse ce tissu et donne des conseils sur les types de vêtements les plus adaptés :

Nom: {fabric_data.get('name', 'Tissu')}
Description: {fabric_data.get('description', 'Non spécifiée')}
Couleur: {fabric_data.get('color', 'Non spécifiée')}
Prix: {fabric_data.get('unit_price', 0)}€/{fabric_data.get('unit_display', 'm')}

Donne une analyse concise et utile en français."""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en textiles. Analyse ce tissu et donne des conseils sur les types de vêtements les plus adaptés."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=300
        )

        analysis = response.choices[0].message.content
        
        return Response({
            'success': True,
            'analysis': analysis,
            'fabric_id': fabric_data.get('id')
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': 'Erreur lors de l\'analyse',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_model_image(request):
    """
    Génère une image pour un modèle avec DALL-E
    """
    try:
        data = request.data
        prompt = data.get('prompt', '')
        
        if not prompt:
            return Response({
                'success': False,
                'error': 'Prompt requis pour la génération d\'image'
            }, status=status.HTTP_400_BAD_REQUEST)

        response = openai.Image.create(
            prompt=f"Professional fashion design: {prompt}, high quality, clean background, fashion photography style",
            n=1,
            size="512x512"
        )

        image_url = response.data[0].url
        
        return Response({
            'success': True,
            'image_url': image_url
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': 'Erreur lors de la génération d\'image',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def generate_models(request):
    """
    Génère des modèles de vêtements basés sur un tissu donné
    Utilise la version gratuite de ChatGPT (GPT-3.5-turbo)
    """
    try:
        data = json.loads(request.body)
        fabric_data = data.get('fabric', {})
        
        # Si pas d'API key, utiliser des modèles prédéfinis
        if not OPENAI_API_KEY:
            return Response({
                'success': True,
                'models': get_fallback_models(fabric_data),
                'message': 'Modèles générés localement (pas d\'API key configurée)'
            })
        
        # Préparer le prompt pour GPT-3.5-turbo
        prompt = create_model_generation_prompt(fabric_data)
        
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': DEFAULT_MODEL,
            'messages': [
                {
                    'role': 'system',
                    'content': 'Tu es un expert en mode et couture. Tu génères des descriptions détaillées de modèles de vêtements.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 800,  # Réduit pour économiser les tokens
            'temperature': 0.7
        }
        
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Parser la réponse AI
            models = parse_ai_response(ai_response, fabric_data)
            
            return Response({
                'success': True,
                'models': models,
                'ai_analysis': f"Analyse AI: {ai_response[:200]}...",
                'model_used': DEFAULT_MODEL
            })
        else:
            # En cas d'erreur API, utiliser les modèles de fallback
            return Response({
                'success': True,
                'models': get_fallback_models(fabric_data),
                'message': f'Erreur API ({response.status_code}), modèles générés localement'
            })
            
    except Exception as e:
        return Response({
            'success': True,
            'models': get_fallback_models(fabric_data),
            'message': f'Erreur: {str(e)}, modèles générés localement'
        }, status=status.HTTP_200_OK)

def create_model_generation_prompt(fabric_data):
    """Crée un prompt optimisé pour GPT-3.5-turbo"""
    fabric_name = fabric_data.get('name', 'tissu')
    fabric_type = fabric_data.get('type', 'standard')
    fabric_color = fabric_data.get('color', 'neutre')
    fabric_price = fabric_data.get('price', 0)
    
    return f"""
    Génère 3-4 modèles de vêtements pour ce tissu:
    - Nom: {fabric_name}
    - Type: {fabric_type}
    - Couleur: {fabric_color}
    - Prix: {fabric_price}€/m
    
    Pour chaque modèle, donne:
    1. Nom du modèle
    2. Description courte (2-3 phrases)
    3. Prix ajusté selon le tissu
    4. Difficulté de réalisation
    
    Format JSON:
    {{
        "models": [
            {{
                "name": "Nom du modèle",
                "description": "Description",
                "price": prix,
                "difficulty": "facile/moyen/difficile"
            }}
        ]
    }}
    """

def parse_ai_response(ai_response, fabric_data):
    """Parse la réponse AI et génère des modèles"""
    try:
        # Essayer de parser le JSON de la réponse AI
        if '{' in ai_response and '}' in ai_response:
            start = ai_response.find('{')
            end = ai_response.rfind('}') + 1
            json_str = ai_response[start:end]
            parsed = json.loads(json_str)
            
            if 'models' in parsed:
                models = []
                for model_data in parsed['models']:
                    base_price = fabric_data.get('price', 50)
                    model_price = model_data.get('price', base_price * 1.5)
                    
                    models.append({
                        'id': f"ai-{len(models) + 1}",
                        'name': model_data.get('name', 'Modèle AI'),
                        'description': model_data.get('description', 'Modèle généré par IA'),
                        'image': '/api/models/placeholder.jpg',
                        'price': model_price,
                        'difficulty': model_data.get('difficulty', 'moyen'),
                        'fabric_required': fabric_data.get('name', 'Tissu'),
                        'ai_generated': True
                    })
                return models
    except:
        pass
    
    # Fallback si parsing échoue
    return get_fallback_models(fabric_data)

def get_fallback_models(fabric_data):
    """Modèles de fallback sans API"""
    fabric_name = fabric_data.get('name', 'Tissu')
    fabric_price = fabric_data.get('price', 50)
    
    models = [
        {
            'id': 'fallback-1',
            'name': f'Robe {fabric_name}',
            'description': f'Robe élégante en {fabric_name.lower()}, parfaite pour toutes occasions',
            'image': '/api/models/placeholder.jpg',
            'price': fabric_price * 2.5,
            'difficulty': 'moyen',
            'fabric_required': fabric_name,
            'ai_generated': False
        },
        {
            'id': 'fallback-2',
            'name': f'Chemise {fabric_name}',
            'description': f'Chemise classique en {fabric_name.lower()}, confortable et stylée',
            'image': '/api/models/placeholder.jpg',
            'price': fabric_price * 1.8,
            'difficulty': 'facile',
            'fabric_required': fabric_name,
            'ai_generated': False
        },
        {
            'id': 'fallback-3',
            'name': f'Pantalon {fabric_name}',
            'description': f'Pantalon moderne en {fabric_name.lower()}, coupe tendance',
            'image': '/api/models/placeholder.jpg',
            'price': fabric_price * 2.2,
            'difficulty': 'moyen',
            'fabric_required': fabric_name,
            'ai_generated': False
        }
    ]
    
    return models

@csrf_exempt
@api_view(['GET'])
def test_connection(request):
    """Test de connexion à l'API ChatGPT"""
    if not OPENAI_API_KEY:
        return Response({
            'status': 'no_api_key',
            'message': 'Aucune clé API configurée. Utilisation des modèles locaux.',
            'model': 'local_fallback'
        })
    
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': DEFAULT_MODEL,
            'messages': [
                {
                    'role': 'user',
                    'content': 'Test de connexion - réponds juste "OK"'
                }
            ],
            'max_tokens': 10
        }
        
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            return Response({
                'status': 'success',
                'message': 'Connexion API réussie',
                'model': DEFAULT_MODEL
            })
        else:
            return Response({
                'status': 'error',
                'message': f'Erreur API: {response.status_code}',
                'model': DEFAULT_MODEL
            })
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Erreur de connexion: {str(e)}',
            'model': DEFAULT_MODEL
        }) 