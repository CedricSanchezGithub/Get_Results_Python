import os
import time

import pandas as pd
from bs4 import BeautifulSoup

from src.scraper.get_match.get_competition_and_day import get_competition_via_url, get_day_via_url


def get_match_results(driver, url):
    """
    Récupère les résultats de match et les informations de l'URL, puis les enregistre dans un fichier CSV unique.
    """
    csv_filename = "results.csv"
    class_name = "styles_rencontre__9O0P0"
    folder = "data"

    # Assurer que le dossier existe
    if not os.path.exists(folder):
        os.makedirs(folder)

    csv_filepath = os.path.join(folder, csv_filename)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")

    # Extraire les informations competition et journee depuis l'URL
    competition = get_competition_via_url(url)
    time.sleep(2)
    journee = get_day_via_url(url)

    # Vérifier si la classe est spécifiée
    if not class_name:
        print("Aucune classe spécifiée. Aucun contenu récupéré.")
        return

    # Rechercher les données dans le HTML
    content = soup.find_all(class_=class_name)
    if not content:
        print(f"Aucune balise avec la classe '{class_name}' trouvée.")
        return

    # Collecte des données de la page actuelle
    data = []
    for match in content:
        try:
            date_time = match.find("p", class_="block_date__dYMQX").text.strip()
            team_1_name = match.find("div", class_="styles_teamName__aH4Gu styles_left__svLY+").text.strip()
            team_1_score = match.find("div", class_="styles_score__ELPXO styles_winner__LkkrE").text.strip()
            team_2_name = match.find("div", class_="styles_teamName__aH4Gu styles_right__wdfIf").text.strip()
            team_2_score = match.find("div", class_="styles_score__ELPXO").text.strip()
            match_link = match["href"]

            # Ajouter les données competition et journee à chaque match
            data.append({
                "date_time": date_time,
                "team_1_name": team_1_name,
                "team_1_score": team_1_score,
                "team_2_name": team_2_name,
                "team_2_score": team_2_score,
                "match_link": match_link,
                "competition": competition,  # Ajout de competition
                "journee": journee           # Ajout de journee
            })
        except AttributeError:
            print("Un des éléments de match est manquant, passage au suivant.")
            continue

    # Convertir les données collectées en DataFrame pandas
    new_data = pd.DataFrame(data)

    # Charger les données existantes si le fichier CSV existe
    if os.path.exists(csv_filepath):
        existing_data = pd.read_csv(csv_filepath)

        # Combiner les anciennes et nouvelles données
        combined_data = pd.concat([existing_data, new_data])

        # Supprimer les doublons éventuels
        combined_data.drop_duplicates(inplace=True)
    else:
        combined_data = new_data

    # Sauvegarder les données combinées dans le fichier CSV
    combined_data.to_csv(csv_filepath, index=False)
    print(f"Données sauvegardées dans le fichier CSV : {csv_filepath}")
