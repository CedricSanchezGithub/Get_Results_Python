import os
import time

import pandas as pd
from bs4 import BeautifulSoup

from src.scraper.get_match.get_competition_and_day import get_competition_via_url, get_day_via_url
from src.scraper.get_match.save_data_csv import save_data


def get_match_results(driver):
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
    competition = get_competition_via_url(driver)
    time.sleep(2)
    day = get_day_via_url(driver)

    # Vérifier si la classe est spécifiée
    if not class_name:
        print("Aucune classe spécifiée. Aucun contenu récupéré.")
        return

    # Rechercher les données dans le HTML
    content = soup.find_all(class_=class_name)
    if not content:
        print(f"Aucune balise avec la classe '{class_name}' trouvée.")
        return

    # DataFrame global pour accumuler toutes les données
    all_data = pd.DataFrame()

    # Collecte des données de la page actuelle
    for match in content:
        try:
            date = match.find("p", class_="block_date__dYMQX").text.strip()
            team_1_name = match.find("div", class_="styles_teamName__aH4Gu styles_left__svLY+").text.strip()
            team_1_score = match.find("div", class_="styles_score__ELPXO styles_winner__LkkrE").text.strip()
            team_2_name = match.find("div", class_="styles_teamName__aH4Gu styles_right__wdfIf").text.strip()
            team_2_score = match.find("div", class_="styles_score__ELPXO").text.strip()
            match_link = match["href"]

            # Ajouter les données competition et journee à chaque match
            all_data = pd.concat([all_data, pd.DataFrame([{
                "date": date,
                "team_1_name": team_1_name,
                "team_1_score": team_1_score,
                "team_2_name": team_2_name,
                "team_2_score": team_2_score,
                "match_link": match_link,
                "competition": competition,
                "journee": day
            }])], ignore_index=True)
        except AttributeError:
            print("Un des éléments de match est manquant, passage au suivant.")
            continue

    # Afficher le DataFrame global à la fin
    print(all_data)

    # Sauvegarder les données combinées dans le fichier CSV
    save_data(csv_filepath, all_data)
