import logging
from bs4 import BeautifulSoup
from src.scraping.get_competition_and_day import get_day_via_url, get_competition_via_url
from src.utils.format_date import format_date


def get_pool_results(driver, category):
    logger = logging.getLogger(__name__)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    competition = get_competition_via_url(driver)
    day = get_day_via_url(driver)

    main_containers = soup.find_all(class_="styles_rencontre__9O0P0")
    if not main_containers:
        logger.warning("Aucune balise trouvée pour la classe 'styles_rencontre__9O0P0'")
        return []

    match_data = []

    for container in main_containers:
        try:
            date_container = container.find("p", class_="block_date__dYMQX")
            date_string = (date_container.text or "").strip() if date_container else None

            if not date_string:
                logger.warning(
                    f"Date introuvable ou vide (category={category}, competition={competition}, journee={day})"
                )
                date_string = "Date non disponible"

            team_left_name, team_left_score = extract_team_data(container, "styles_left__svLY+")
            team_right_name, team_right_score = extract_team_data(container, "styles_right__wdfIf")
            match_link = container.get("href", None)
            formatted_date = format_date(date_string)

            match_data.append({
                "match_date": formatted_date,
                "team_1_name": team_left_name,
                "team_1_score": team_left_score,
                "team_2_name": team_right_name,
                "team_2_score": team_right_score,
                "match_link": match_link,
                "competition": competition,
                "journee": day
            })

        except Exception as e:

            logger.error(
                f"Erreur lors du traitement d'un conteneur (category={category}, competition={competition}, journee={day}): {e}",
                exc_info=True
            )
            continue

    return match_data


def extract_team_data(container, side_class):
    team_container = container.find("div", class_=side_class)
    if not team_container:
        return "Nom non disponible", None

    team_name_element = team_container.find("div", class_="styles_teamName__aH4Gu")
    team_name = team_name_element.text.strip() if team_name_element else "Nom non disponible"

    team_score_element = team_container.find("div", class_="styles_score__ELPXO")
    team_score = team_score_element.text.strip() if team_score_element else "-"

    return team_name, team_score
