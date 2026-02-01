import logging
import time
import requests
from typing import List

from src.models.models import MatchIngest
from src.settings import get_backend_settings

logger = logging.getLogger(__name__)


class IngestClient:
    # Codes HTTP pour lesquels on ne retry pas (erreurs client)
    NON_RETRYABLE_STATUS_CODES = {400, 401, 403, 404, 422}

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        """
        Args:
            max_retries: Nombre maximum de tentatives (défaut: 3)
            base_delay: Délai initial en secondes pour le backoff exponentiel (défaut: 1.0)
        """
        backend_settings = get_backend_settings()
        self.api_url = backend_settings.api_url
        self.api_key = backend_settings.api_key
        self.max_retries = max_retries
        self.base_delay = base_delay

        if not self.api_key:
            logger.warning("⚠️ Aucune API KEY définie (BACKEND_API_KEY). Les requêtes risquent d'échouer (401/403).")

        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "GetResults-Scraper/1.0"
        })

    def _is_retryable_error(self, response: requests.Response = None, exception: Exception = None) -> bool:
        """Détermine si l'erreur justifie un retry."""
        if exception is not None:
            # Erreurs réseau = toujours retry
            return True
        if response is not None:
            # Erreurs 5xx = retry, erreurs 4xx = non
            return response.status_code >= 500

        return False

    def send_matches(self, matches: List[MatchIngest]) -> bool:
        """
        Envoie un batch de matchs au backend avec retry automatique.
        Retourne True si succès, False sinon.
        """
        if not matches:
            return True

        payload = [m.model_dump(mode='json') for m in matches]
        last_exception = None
        last_response = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"📤 Envoi de {len(matches)} matchs vers {self.api_url} (tentative {attempt}/{self.max_retries})...")
                response = self.session.post(self.api_url, json=payload, timeout=10)

                if response.status_code in (200, 201):
                    logger.info("✅ Ingestion réussie.")
                    return True

                last_response = response

                # Erreur non-retryable : on abandonne immédiatement
                if response.status_code in self.NON_RETRYABLE_STATUS_CODES:
                    if response.status_code == 403:
                        logger.error("⛔ Accès refusé (403). Vérifiez BACKEND_API_KEY.")
                    else:
                        logger.error(f"❌ Erreur Backend ({response.status_code}): {response.text}")
                    return False

                # Erreur retryable (5xx) : on continue
                logger.warning(f"⚠️ Erreur serveur ({response.status_code}), retry possible...")

            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(f"⚠️ Erreur réseau : {e}")

            # Backoff exponentiel avant le prochain retry (sauf si dernière tentative)
            if attempt < self.max_retries:
                delay = self.base_delay * (2 ** (attempt - 1))  # 1s, 2s, 4s...
                logger.info(f"⏳ Attente de {delay:.1f}s avant retry...")
                time.sleep(delay)

        # Toutes les tentatives ont échoué
        if last_exception:
            logger.error(f"🔥 Échec définitif après {self.max_retries} tentatives. Dernière erreur : {last_exception}")
        elif last_response:
            logger.error(f"🔥 Échec définitif après {self.max_retries} tentatives. Dernier status : {last_response.status_code}")

        return False