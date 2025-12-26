import logging
import sys
import os

# Setup des chemins pour que Python trouve 'src'
sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.scraping.get_match_results import fetch_html
from src.utils.logging_config import configure_logging

# Config logs
configure_logging()
logger = logging.getLogger("DEBUG_RANKING")


def run_capture():
    # URL Cible : Une poule active (exemple pris dans ton urls.py)
    # Je prends une URL de championnat standard
    target_url = "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/16-ans-f-prenationale-28365/poule-169120/journee-1/"

    logger.info(f"🚀 Démarrage capture HTML pour analyse Classement")

    # 1. Capture de la page 'Journée' (celle que tu as déjà)
    logger.info("📸 Capture URL Journée...")
    fetch_html(target_url, save_debug=True, debug_prefix="JOURNEE_1")

    # 2. Capture de la page 'Poule' (souvent là où est le classement complet)
    # On enlève "journee-1/" de l'URL
    if "journee-" in target_url:
        pool_url = target_url.split("journee-")[0]
        logger.info(f"📸 Capture URL Poule racine : {pool_url}")
        fetch_html(pool_url, save_debug=True, debug_prefix="POULE_RACINE")

    logger.info("✅ Terminé. Vérifie le dossier data/debug_html/")


if __name__ == "__main__":
    run_capture()