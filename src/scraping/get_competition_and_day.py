import os
import pandas as pd

def get_competition_via_url(driver):
    """
    Extrait la compétition de l'URL actuelle du navigateur Selenium.
    """
    url = driver.current_url
    parts = url.split('/')
    competition = parts[-4]
    return competition


def get_day_via_url(driver):
    """
    Extrait la journée de l'URL actuelle du navigateur Selenium.
    """
    url = driver.current_url
    parts = url.split('/')
    journee = parts[-2]
    return journee



def save_to_csv(csv_filepath, competition, journee):
    """
    Enregistre les informations dans un fichier CSV avec pandas.
    Ajoute les nouvelles données sans écraser celles existantes.
    """
    new_data = pd.DataFrame([{"competition": competition, "journee": journee}])

    if os.path.isfile(csv_filepath):
        existing_data = pd.read_csv(csv_filepath)
        combined_data = pd.concat([existing_data, new_data])
        combined_data.drop_duplicates(inplace=True)
    else:
        combined_data = new_data

    combined_data.to_csv(csv_filepath, index=False)
    print(f"Informations enregistrées : {competition}, {journee} dans {csv_filepath}")
