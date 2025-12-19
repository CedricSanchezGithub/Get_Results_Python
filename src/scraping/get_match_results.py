import requests
import json
import html
import logging
import re
from bs4 import BeautifulSoup
from datetime import datetime


def fetch_html(url):
    """Récupère le HTML brut via requests avec des headers navigateur."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.getLogger(__name__).error(f"Erreur réseau sur {url} : {e}")
        return None


def get_matches_from_url(url, category):
    """
    Scrape les résultats des matchs depuis une URL FFHandball.

    Cette fonction extrait les données des rencontres via le composant JSON 'competitions---rencontre-list'.

    Règles métier appliquées :
      - Filtrage strict : Tout match sans date valide ou avec une date "non disponible" est
        immédiatement ignoré pour garantir l'intégrité de la base de données (prévention des NULLs).
      - Pagination : Tente de récupérer les métadonnées des autres journées via les sélecteurs de poule.

    Args:
        url (str): L'URL cible de la journée à scraper.
        category (str): La catégorie (ex: 'SF', '-18F') associée à ces matchs.

    Returns:
        tuple: (match_data, journees_meta)
            - match_data (list): Liste de dictionnaires des matchs valides.
            - journees_meta (list): Liste brute des journées disponibles pour la navigation.
    """

    logger = logging.getLogger(__name__)
    html_content = fetch_html(url)

    if not html_content:
        return [], []

    soup = BeautifulSoup(html_content, "html.parser")

    match_data = []
    rencontre_component = soup.find("smartfire-component", attrs={"name": "competitions---rencontre-list"})

    current_journee_match = re.search(r"journee-(\d+)", url)
    current_journee = current_journee_match.group(1) if current_journee_match else None

    if rencontre_component:
        try:
            raw_attr = rencontre_component.get("attributes", "{}")
            json_data = json.loads(html.unescape(raw_attr))
            rencontres = json_data.get("rencontres", [])

            for match in rencontres:
                raw_date = match.get("date")
                formatted_date = None
                if raw_date:
                    try:
                        formatted_date = datetime.fromisoformat(raw_date).strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass
                if not formatted_date:
                    logger.warning(
                        f"Match ignoré (Date absente) : {match.get('equipe1Libelle')} vs {match.get('equipe2Libelle')}")
                    continue
                # ---------------------------

                match_entry = {
                    "match_date": formatted_date,
                    "team_1_name": match.get("equipe1Libelle", "Nom non disponible"),
                    "team_1_score": match.get("equipe1Score") if match.get("equipe1Score") != "" else None,
                    "team_2_name": match.get("equipe2Libelle", "Nom non disponible"),
                    "team_2_score": match.get("equipe2Score") if match.get("equipe2Score") != "" else None,
                    "match_link": None,
                    "competition": category,
                    "journee": match.get("journeeNumero", current_journee)
                }
                match_data.append(match_entry)

        except Exception as e:
            logger.error(f"Erreur parsing JSON rencontres pour {category}: {e}")

    journees_meta = []
    selector_component = soup.find("smartfire-component", attrs={"name": "competitions---poule-selector"})

    if not selector_component:
        selector_component = soup.find("smartfire-component", attrs={"name": "competitions---journee-selector"})

    if selector_component:
        try:
            raw_attr = selector_component.get("attributes", "{}")

            main_json = json.loads(html.unescape(raw_attr))
            raw_journees = main_json.get("journees")
            if not raw_journees and "poule" in main_json:
                raw_journees = main_json["poule"].get("journees")
            if not raw_journees and "selected_poule" in main_json:
                raw_journees = main_json["selected_poule"].get("journees")

            if isinstance(raw_journees, str):
                journees_meta = json.loads(raw_journees)
            elif isinstance(raw_journees, list):
                journees_meta = raw_journees

        except Exception as e:
            logger.warning(f"Impossible d'extraire la liste des journées pour {category}: {e}")

    return match_data, journees_meta