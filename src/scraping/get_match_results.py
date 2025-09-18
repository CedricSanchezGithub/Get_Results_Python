import locale
import os
from datetime import datetime
import logging

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
                "date_string": parse_date_to_milliseconds(date_string),
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


def parse_date_to_milliseconds(date_string):
    """
    Convertit une date française de type "samedi 07 septembre 2024 à 14H00"
    en timestamp (millisecondes). Retourne None si invalide.
    """
    # Validation d'entrée
    if not date_string or not isinstance(date_string, str):
        logging.getLogger(__name__).warning("Date invalide ou vide")
        return None

    original = date_string

    # Normalisation simple: retirer " à ", transformer 14H00 -> 14:00
    date_string = date_string.replace(" à ", " ").replace("H", ":")

    # Certaines locales fr_FR ne sont pas installées dans les conteneurs minimalistes.
    # On tente d'abord avec la locale fr_FR, sinon on fait un mapping manuel des mois.
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        try:
            dt = datetime.strptime(date_string, "%A %d %B %Y %H:%M")
            return int(dt.timestamp() * 1000)
        except ValueError:
            pass  # on retombera sur le fallback
    except Exception:
        # Locale indisponible: on passe au fallback
        pass

    # Fallback: mapping manuel des mois français vers nombres
    months = {
        'janvier': '01', 'février': '02', 'fevrier': '02', 'mars': '03', 'avril': '04',
        'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08', 'aout': '08',
        'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12', 'decembre': '12'
    }

    # Exemple attendu après normalisation: "samedi 07 septembre 2024 14:00"
    parts = date_string.strip().split()
    # On s'attend à: [jour_semaine, jour, mois, annee, heure]
    if len(parts) >= 5:
        # garder les 5 premiers éléments (au cas où des tokens en plus)
        _, day, month_name, year, time_part = parts[0], parts[1], parts[2].lower(), parts[3], parts[4]
        month_num = months.get(month_name)
        if month_num:
            try:
                # Construire une chaîne au format ISO: YYYY-MM-DD HH:MM
                norm = f"{year}-{day.zfill(2)}-{month_num} {time_part}"
                dt = datetime.strptime(norm, "%Y-%d-%m %H:%M")
                return int(dt.timestamp() * 1000)
            except ValueError as e:
                logging.getLogger(__name__).warning(f"Erreur parsing fallback pour '{original}' → '{norm}': {e}")
        else:
            logging.getLogger(__name__).warning(f"Mois inconnu dans la date: '{month_name}' (original: '{original}')")
    else:
        logging.getLogger(__name__).warning(f"Format inattendu pour la date: '{original}'")

    return None