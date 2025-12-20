import os
import requests
import logging
import time


def get_urls_from_api():
    """
    Récupère les compétitions actives depuis l'API Backend.
    Gère les tentatives de reconnexion si le backend n'est pas encore prêt.
    """
    logger = logging.getLogger(__name__)

    api_url = os.getenv("API_URL")

    max_retries = 3
    retry_delay = 5  # secondes

    for attempt in range(max_retries):
        try:
            logger.info(f"Tentative {attempt + 1}/{max_retries} : Récupération des URLs depuis {api_url}")
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()

            data = response.json()
            logger.info(f"✅ Succès : {len(data)} compétitions actives récupérées.")
            return data

        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Échec de connexion à l'API : {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error(
                    "❌ Impossible de joindre l'API après plusieurs tentatives. Vérifiez que le service 'backend' est en ligne.")
                return []
    return []