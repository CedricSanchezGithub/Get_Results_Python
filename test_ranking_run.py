import logging
from src.scraping.get_all import get_all
from src.utils.logging_config import configure_logging

configure_logging()

# Une URL valide où on sait qu'il y a un classement (celle que tu as debuggée)
URL_TEST = "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/16-ans-f-prenationale-28365/poule-169120/journee-1/"
CATEGORIE_TEST = "TEST_DEBUG_RANKING"

if __name__ == "__main__":
    print("🚀 Lancement du test manuel Classement...")
    get_all(URL_TEST, CATEGORIE_TEST)
    print("✅ Test terminé. Vérifie la table 'ranking' dans ta BDD !")