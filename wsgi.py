import os
from django.core.wsgi import get_wsgi_application
from pathlib import Path

# Ajouter le chemin du projet au PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

application = get_wsgi_application()

# Pour Vercel
app = application 
