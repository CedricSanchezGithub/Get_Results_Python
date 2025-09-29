import os
from src.config import DATA_DIR # Utilise ta constante centralisée

def purge_csv(category):
    csv_filename = f"pool_{category}.csv"
    csv_filepath = os.path.join(DATA_DIR, csv_filename)

    if os.path.exists(csv_filepath):
        os.remove(csv_filepath)
        print(f"Removed old CSV: {csv_filepath}")