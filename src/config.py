import os

# Répertoire racine du projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Définis les chemins à partir de la racine
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DEBUG_DIR = os.path.join(DATA_DIR, "debug_html")
os.makedirs(DEBUG_DIR, exist_ok=True)