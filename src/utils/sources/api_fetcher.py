import os
import requests
import logging
import time


def get_urls_from_api():
    logger = logging.getLogger(__name__)

    api_url = os.getenv("API_URL", "http://backend:8081/api/competitions/active")
    api_key = os.getenv("API_KEY", "secret_local_dev")

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            logger.info(f"Tentative {attempt + 1}/{max_retries} : Appel API vers {api_url}")

            response = requests.get(api_url, headers=headers, timeout=10)

            if response.status_code == 403:
                logger.error("❌ Erreur 403 Forbidden : Clé API refusée.")
                return []

            response.raise_for_status()

            data = response.json()
            logger.info(f"✅ Succès : {len(data)} sources actives reçues.")
            return data

        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Échec connexion API : {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("❌ Abandon après plusieurs échecs.")
                return []
    return []