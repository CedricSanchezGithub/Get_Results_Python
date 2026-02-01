"""
Rate limiter pour éviter de surcharger les serveurs FFHandball.
Utilise un token bucket avec délai minimum entre les requêtes.
"""
import threading
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter thread-safe avec délai minimum entre les requêtes.

    Utilisation:
        limiter = RateLimiter(min_delay=1.0)
        limiter.wait()  # Attend si nécessaire avant la prochaine requête
    """

    _instance: Optional['RateLimiter'] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Singleton pattern pour partager le limiter entre tous les threads."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, min_delay: float = 1.0, burst_limit: int = 5, burst_window: float = 10.0):
        """
        Args:
            min_delay: Délai minimum entre deux requêtes (secondes)
            burst_limit: Nombre max de requêtes dans la fenêtre burst
            burst_window: Fenêtre de temps pour le burst (secondes)
        """
        if self._initialized:
            return

        self._min_delay = min_delay
        self._burst_limit = burst_limit
        self._burst_window = burst_window
        self._last_request_time = 0.0
        self._request_times: list = []
        self._request_lock = threading.Lock()
        self._initialized = True

        logger.info(f"RateLimiter initialisé: min_delay={min_delay}s, burst={burst_limit}/{burst_window}s")

    def wait(self) -> float:
        """
        Attend si nécessaire avant d'autoriser une nouvelle requête.

        Returns:
            Temps d'attente effectif (secondes)
        """
        with self._request_lock:
            now = time.time()
            waited = 0.0

            # 1. Vérifier le délai minimum depuis la dernière requête
            time_since_last = now - self._last_request_time
            if time_since_last < self._min_delay:
                wait_time = self._min_delay - time_since_last
                time.sleep(wait_time)
                waited += wait_time
                now = time.time()

            # 2. Nettoyer les anciennes requêtes hors de la fenêtre burst
            cutoff = now - self._burst_window
            self._request_times = [t for t in self._request_times if t > cutoff]

            # 3. Si burst limit atteint, attendre que la fenêtre se libère
            if len(self._request_times) >= self._burst_limit:
                oldest = self._request_times[0]
                wait_until = oldest + self._burst_window
                if wait_until > now:
                    extra_wait = wait_until - now
                    logger.debug(f"Burst limit atteint, attente {extra_wait:.2f}s")
                    time.sleep(extra_wait)
                    waited += extra_wait
                    now = time.time()
                    # Re-nettoyer après l'attente
                    cutoff = now - self._burst_window
                    self._request_times = [t for t in self._request_times if t > cutoff]

            # 4. Enregistrer cette requête
            self._request_times.append(now)
            self._last_request_time = now

            if waited > 0:
                logger.debug(f"RateLimiter: attendu {waited:.2f}s")

            return waited

    def reset(self):
        """Réinitialise le rate limiter (utile pour les tests)."""
        with self._request_lock:
            self._last_request_time = 0.0
            self._request_times.clear()


# Instance globale par défaut
_default_limiter: Optional[RateLimiter] = None


def get_rate_limiter(min_delay: float = 1.0) -> RateLimiter:
    """Récupère ou crée le rate limiter global."""
    global _default_limiter
    if _default_limiter is None:
        _default_limiter = RateLimiter(min_delay=min_delay)
    return _default_limiter


def rate_limited_request(func):
    """
    Décorateur pour appliquer le rate limiting à une fonction de requête.

    Usage:
        @rate_limited_request
        def fetch_data(url):
            return requests.get(url)
    """
    def wrapper(*args, **kwargs):
        limiter = get_rate_limiter()
        limiter.wait()
        return func(*args, **kwargs)
    return wrapper
