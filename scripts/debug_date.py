import sys
import os
import json
import html
import logging
from bs4 import BeautifulSoup

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scraping.get_match_results import fetch_html
from src.utils.format_date import format_date
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("DEBUG_DATE")


def debug_dates(url):
    logger.info(f"🔍 ANALYSE DE L'URL : {url}")

    # 1. Récupération HTML (On utilise ta fonction pour être iso-prod)
    html_content = fetch_html(url)
    if not html_content:
        logger.error("❌ Impossible de récupérer le HTML.")
        return

    soup = BeautifulSoup(html_content, "html.parser")

    # 2. Ciblage du composant JSON
    component = soup.find("smartfire-component", attrs={"name": "competitions---rencontre-list"})

    if not component:
        logger.error("❌ Composant 'competitions---rencontre-list' introuvable.")
        return

    # 3. Extraction de la donnée BRUTE
    try:
        raw_attributes = component.get("attributes", "{}")
        json_data = json.loads(html.unescape(raw_attributes))
        rencontres = json_data.get("rencontres", [])
    except Exception as e:
        logger.error(f"❌ Erreur parsing JSON : {e}")
        return

    logger.info(f"👉 {len(rencontres)} matchs trouvés dans le JSON brut.\n")
    logger.info(f"{'DATE BRUTE (JSON)':<40} | {'DATE PARSÉE (Objet datetime)':<35} | {'STATUS'}")
    logger.info("-" * 90)

    for match in rencontres:
        raw_date = match.get("date")
        parsed_dt = format_date(raw_date)

        db_value = parsed_dt.strftime("%Y-%m-%d %H:%M:%S") if parsed_dt else "None (REJETÉ)"
        status = "✅ OK" if parsed_dt else "❌ KO"
        display_raw = (raw_date[:37] + '...') if raw_date and len(raw_date) > 37 else raw_date
        logger.info(f"{str(display_raw):<40} | {str(db_value):<35} | {status}")

        if not parsed_dt and raw_date:
            # Si échec, on analyse pourquoi (caractères invisibles ?)
            logger.info(f"   ⚠️  Détail échec : Type='{type(raw_date)}' Valeur_Repr={repr(raw_date)}")


if __name__ == "__main__":
    base_url = "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/16-ans-f-prenationale-28365/poule-169120/journee-"
    for i in range(1, 10):
        URL_CIBLE = base_url + str(i)
        debug_dates(URL_CIBLE)
