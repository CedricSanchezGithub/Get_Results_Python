import logging
import requests
import json
import html
from bs4 import BeautifulSoup
from datetime import datetime

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_scraping_requests():
    # URL cible
    url = "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/16-ans-f-prenationale-28365/poule-169120/journee-1/"

    # Headers pour imiter un vrai navigateur (évite les blocages basiques)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    logger.info(f"--- DÉBUT DU TEST (MODE REQUESTS) ---")
    logger.info(f"GET {url}...")

    try:
        # 1. Récupération du code source BRUT (sans exécution JS)
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Lève une erreur si 404/500

        html_content = response.text
        logger.info(f"Réponse reçue : {len(html_content)} caractères.")

        # 2. Parsing HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # 3. Recherche du composant
        component = soup.find("smartfire-component", attrs={"name": "competitions---rencontre-list"})

        if not component:
            logger.error("❌ ÉCHEC : Composant 'competitions---rencontre-list' introuvable dans le source brut.")
            # Debug : vérifier si on est bloqué ou si la page est différente
            logger.info("Snippet du HTML reçu :")
            logger.info(html_content[:500])
            return

        logger.info("✅ Composant trouvé !")

        # 4. Extraction JSON
        raw_attributes = component.get("attributes", "{}")
        json_data = json.loads(html.unescape(raw_attributes))
        rencontres = json_data.get("rencontres", [])

        if rencontres:
            logger.info(f"✅ SUCCÈS ! {len(rencontres)} matchs trouvés dans le JSON.")
            logger.info("-" * 50)
            for match in rencontres:
                # Petit formatage pour la gloire
                raw_date = match.get("date")
                dt_str = raw_date
                try:
                    dt_str = datetime.fromisoformat(raw_date).strftime("%d/%m/%Y %H:%M")
                except:
                    pass

                score = f"{match.get('equipe1Score')} - {match.get('equipe2Score')}"
                match_line = f"📅 {dt_str} | 🤾 {match.get('equipe1Libelle'):<30} {score:^10} {match.get('equipe2Libelle')}"
                logger.info(match_line)
            logger.info("-" * 50)
        else:
            logger.warning("⚠️ Composant trouvé mais liste 'rencontres' vide.")

    except Exception as e:
        logger.error(f"❌ CRASH : {e}")


if __name__ == "__main__":
    test_scraping_requests()