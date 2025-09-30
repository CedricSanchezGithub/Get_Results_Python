import os
import logging

import pandas as pd
from bs4 import BeautifulSoup

from src.config import DATA_DIR
from src.scraping.get_competition_and_day import get_day_via_url, get_competition_via_url
from src.saving.save_data_csv import save_data
from src.utils.format_date import format_date


def get_pool_results(driver, category):
    csv_filename = f"pool_{category}.csv"
    os.makedirs(DATA_DIR, exist_ok=True)
    csv_filepath = os.path.join(DATA_DIR, csv_filename)

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
            if date_container is None:
                logger.warning(
                    f"Date: balise <p class='block_date__dYMQX'> introuvable (category={category}, competition={competition}, journee={day})"
                )
                date_string = "Aucune date"
            else:
                raw = (date_container.text or "").strip()
                if not raw:
                    logger.warning(
                        f"Date: balise présente mais vide (category={category}, competition={competition}, journee={day})"
                    )
                    date_string = "Aucune date"
                else:
                    date_string = raw
                    logger.info(f"Date récupérée (brute)='{date_string}' (category={category}, competition={competition}, journee={day})")
                    # Tentative de parsing pour journaliser le format; n'altère pas la valeur stockée
                    iso = format_date(date_string)
                    if iso:
                        logger.info(f"Date parsée en ISO='{iso}'")
                    else:
                        logger.warning("Impossible de parser la date (voir logs format_date pour détails)")

            team_left_name, team_left_score = extract_team_data(container, "styles_left__svLY+")
            team_right_name, team_right_score = extract_team_data(container, "styles_right__wdfIf")
            match_link = container.get("href", None)

            match_data.append({
                "match_date": date_string,
                "team_1_name": team_left_name,
                "team_1_score": team_left_score,
                "team_2_name": team_right_name,
                "team_2_score": team_right_score,
                "match_link": match_link,
                "competition": competition,
                "journee": day
            })

        except AttributeError as e:
            logger.error(
                f"Erreur dans un conteneur (category={category}, competition={competition}, journee={day}): {e}")
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
