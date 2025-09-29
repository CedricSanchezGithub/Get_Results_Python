import locale
import os
from datetime import datetime
import logging
from typing import Union

import pandas as pd
from bs4 import BeautifulSoup

from src.scraping.get_competition_and_day import get_day_via_url, get_competition_via_url
from src.saving.save_data_csv import save_data


def get_pool_results(driver, category):

    csv_filename = f"pool_{category}.csv"
    folder = "data"
    os.makedirs(folder, exist_ok=True)
    csv_filepath = os.path.join(folder, csv_filename)

    logger = logging.getLogger(__name__)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    competition = get_competition_via_url(driver)
    day = get_day_via_url(driver)

    main_containers = soup.find_all(class_="styles_rencontre__9O0P0")
    if not main_containers:
        logger.warning("Aucune balise trouvée pour la classe 'styles_rencontre__9O0P0'")
        return

    match_data = []

    for container in main_containers:
        try:
            date_container = container.find("p", class_="block_date__dYMQX")
            date_string = date_container.text.strip() if date_container else None
            team_left_name, team_left_score = extract_team_data(container, "styles_left__svLY+")
            team_right_name, team_right_score = extract_team_data(container, "styles_right__wdfIf")
            match_link = container.get("href", None)

            match_data.append({
                "match_date": parse_date_to_milliseconds(date_string),
                "team_1_name": team_left_name,
                "team_1_score": team_left_score,
                "team_2_name": team_right_name,
                "team_2_score": team_right_score,
                "match_link": match_link,
                "competition": competition,
                "journee": day
            })

        except AttributeError as e:
            logger.error(f"Erreur dans un conteneur (category={category}, competition={competition}, journee={day}): {e}")
            continue

    all_data = pd.DataFrame(match_data)

    save_data(csv_filepath, all_data)


def extract_team_data(container, side_class):

    team_container = container.find("div", class_=side_class)
    if not team_container:
        return "Nom non disponible", None

    # Nom de l'équipe
    team_name = (
        team_container.find("div", class_="styles_teamName__aH4Gu").text.strip()
        if team_container.find("div", class_="styles_teamName__aH4Gu")
        else "Nom non disponible"
    )

    # Score de l'équipe
    team_score = (
        team_container.find("div", class_="styles_score__ELPXO").text.strip()
        if team_container.find("div", class_="styles_score__ELPXO")
        else "-"
    )

    return team_name, team_score


def parse_date_to_milliseconds(date_string: str) -> Union[int, None]:
    """
    Convertit une date française de type "samedi 07 septembre 2024 à 14H00"
    en timestamp (millisecondes). Retourne None si invalide.
    """
    if not date_string or not isinstance(date_string, str):
        logging.getLogger(__name__).warning("Date invalide ou vide fournie.")
        return None

    # 1. Nettoyage et normalisation
    date_string = date_string.lower().replace(" à ", " ").replace("h", ":")

    # 2. Mapping des mois (robuste et indépendant de la locale)
    months = {
        'janvier': '01', 'février': '02', 'fevrier': '02', 'mars': '03',
        'avril': '04', 'mai': '05', 'juin': '06', 'juillet': '07',
        'août': '08', 'aout': '08', 'septembre': '09', 'octobre': '10',
        'novembre': '11', 'décembre': '12', 'decembre': '12'
    }

    # 3. Remplacement du nom du mois par son numéro
    for name, number in months.items():
        if name in date_string:
            date_string = date_string.replace(name, number)
            break
    else:
        logging.getLogger(__name__).warning(f"Mois non trouvé dans la date : '{date_string}'")
        return None

    # 4. Extraction et conversion
    parts = date_string.split()
    if len(parts) < 4:
        logging.getLogger(__name__).warning(f"Format de date inattendu après traitement : '{date_string}'")
        return None

    try:
        # Format : jour mois annee heure:minute
        date_to_parse = " ".join(parts[1:5])
        dt_format = "%d %m %Y %H:%M"
        dt_object = datetime.strptime(date_to_parse, dt_format)
        return int(dt_object.timestamp() * 1000)
    except (ValueError, IndexError) as e:
        logging.getLogger(__name__).error(f"Échec final du parsing de la date '{date_string}': {e}")
        return None