import os
import subprocess
import sys

def build():
    # Installer les dépendances
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Collecter les fichiers statiques
    subprocess.check_call([sys.executable, "manage.py", "collectstatic", "--noinput"])
    
    # Appliquer les migrations
    subprocess.check_call([sys.executable, "manage.py", "migrate"])
    
    print("Build completed successfully!")

if __name__ == "__main__":
    build() 