import os
import pandas as pd
import time


# def get_day_and_competition(driver):
#     """
#     Extrait les informations de l'URL et les enregistre dans un fichier CSV.
#     """
#     # Extraire les informations
#     competition = get_competition_via_url(driver)
#     time.sleep(2)
#     journee = get_day_via_url(driver)
#
#     # Préparer le dossier et le fichier
#     folder = "data"
#     csv_filename = "day_and_competition.csv"
#     os.makedirs(folder, exist_ok=True)
#     csv_filepath = os.path.join(folder, csv_filename)
#
#     # Enregistrer dans le CSV
#     save_to_csv(csv_filepath, competition, journee)


def get_competition_via_url(driver):
    """
    Extrait la compétition de l'URL actuelle du navigateur Selenium.
    """
    url = driver.current_url  # Récupère l'URL actuelle via Selenium
    print("Extracting competition from URL")
    parts = url.split('/')
    competition = parts[-4]  # Adapte la position en fonction de l'URL réelle
    return competition


def get_day_via_url(driver):
    """
    Extrait la journée de l'URL actuelle du navigateur Selenium.
    """
    url = driver.current_url  # Récupère l'URL actuelle via Selenium
    print("Extracting journee from URL")
    parts = url.split('/')
    journee = parts[-2]  # Adapte la position en fonction de l'URL réelle
    return journee



def save_to_csv(csv_filepath, competition, journee):
    """
    Enregistre les informations dans un fichier CSV avec pandas.
    Ajoute les nouvelles données sans écraser celles existantes.
    """
    # Créer un DataFrame pour les nouvelles données
    new_data = pd.DataFrame([{"competition": competition, "journee": journee}])

    if os.path.isfile(csv_filepath):
        # Charger les données existantes
        existing_data = pd.read_csv(csv_filepath)

        # Combiner les nouvelles données avec les existantes
        combined_data = pd.concat([existing_data, new_data])

        # Supprimer les doublons éventuels
        combined_data.drop_duplicates(inplace=True)
    else:
        # Si le fichier n'existe pas, les nouvelles données sont les seules présentes
        combined_data = new_data

    # Sauvegarder les données combinées
    combined_data.to_csv(csv_filepath, index=False)
    print(f"Informations enregistrées : {competition}, {journee} dans {csv_filepath}")
