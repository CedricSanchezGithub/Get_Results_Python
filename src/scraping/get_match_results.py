import requests
import json
import html
import logging
import re
from bs4 import BeautifulSoup
from datetime import datetime

from src.scraping.get_competition_and_day import get_competition_via_url


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
    Scrape une URL FFHandball.
    Retourne :
      - match_data : Liste des matchs trouvés.
      - journees_meta : Liste brute des journées disponibles (pour la pagination).
    """
    logger = logging.getLogger(__name__)
    html_content = fetch_html(url)

    if not html_content:
        return [], []

    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Extraction des Matchs (via competitions---rencontre-list)
    match_data = []
    rencontre_component = soup.find("smartfire-component", attrs={"name": "competitions---rencontre-list"})

    # Récupération contextuelle (Competition / Journée)
    # On essaie de parser l'URL, sinon on prendra ce qu'il y a dans le JSON
    # Le numéro de journée est souvent dans l'URL ex: /journee-3/
    current_journee_match = re.search(r"journee-(\d+)", url)
    current_journee = current_journee_match.group(1) if current_journee_match else None

    if rencontre_component:
        try:
            raw_attr = rencontre_component.get("attributes", "{}")
            json_data = json.loads(html.unescape(raw_attr))
            rencontres = json_data.get("rencontres", [])

            for match in rencontres:
                # Parsing date
                raw_date = match.get("date")
                formatted_date = None
                if raw_date:
                    try:
                        formatted_date = datetime.fromisoformat(raw_date).strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass

                match_entry = {
                    "match_date": formatted_date,
                    "team_1_name": match.get("equipe1Libelle", "Nom non disponible"),
                    "team_1_score": match.get("equipe1Score") if match.get("equipe1Score") != "" else None,
                    "team_2_name": match.get("equipe2Libelle", "Nom non disponible"),
                    "team_2_score": match.get("equipe2Score") if match.get("equipe2Score") != "" else None,
                    "match_link": None,
                    "competition": category,  # On utilise la catégorie comme clé de compétition principale ici
                    "journee": match.get("journeeNumero", current_journee)
                }
                match_data.append(match_entry)
        except Exception as e:
            logger.error(f"Erreur parsing JSON rencontres pour {category}: {e}")

    # 2. Extraction des Journées (pour la pagination future)
    # On cherche le composant qui contient la liste des journées (souvent poule-selector ou journee-selector)
    journees_meta = []
    selector_component = soup.find("smartfire-component", attrs={"name": "competitions---poule-selector"})

    # Fallback si poule-selector n'existe pas (parfois journee-selector)
    if not selector_component:
        selector_component = soup.find("smartfire-component", attrs={"name": "competitions---journee-selector"})

    if selector_component:
        try:
            raw_attr = selector_component.get("attributes", "{}")
            # Parfois "journees" est une string JSON échappée à l'intérieur du JSON...
            # Il faut inspecter la structure. Souvent: attributes='{"poule": {"journees": "[...]"}}'
            # Ou attributes='{"journees": "[...]"}'

            # Décodage niveau 1
            main_json = json.loads(html.unescape(raw_attr))

            # Recherche de la clé "journees"
            # Parfois directe, parfois dans "poule" ou "selected_poule"
            raw_journees = main_json.get("journees")
            if not raw_journees and "poule" in main_json:
                raw_journees = main_json["poule"].get("journees")
            if not raw_journees and "selected_poule" in main_json:
                raw_journees = main_json["selected_poule"].get("journees")

            # Si raw_journees est une string (double encoding fréquent chez Smartfire), on re-parse
            if isinstance(raw_journees, str):
                journees_meta = json.loads(raw_journees)
            elif isinstance(raw_journees, list):
                journees_meta = raw_journees

        except Exception as e:
            logger.warning(f"Impossible d'extraire la liste des journées pour {category}: {e}")

    return match_data, journees_meta