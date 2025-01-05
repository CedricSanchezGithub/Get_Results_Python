# Charger les données existantes si le fichier CSV existe
import os

import pandas as pd


def save_data(csv_filepath, all_data):

    if os.path.exists(csv_filepath):
        existing_data = pd.read_csv(csv_filepath)
        combined_data = pd.concat([existing_data, all_data], ignore_index=True)  #

        combined_data.drop_duplicates(inplace=True)
    else:
        combined_data = all_data

    # Sauvegarder les données combinées dans le fichier CSV
    combined_data.to_csv(csv_filepath, index=False)
    print(f"Données sauvegardées dans le fichier CSV : {csv_filepath}")
