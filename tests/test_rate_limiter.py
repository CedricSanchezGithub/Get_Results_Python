import pytest
import time
import threading
from unittest.mock import patch


class TestRateLimiter:
    """Tests pour le rate limiter."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset le singleton entre chaque test."""
        from src.utils import rate_limiter
        rate_limiter.RateLimiter._instance = None
        rate_limiter._default_limiter = None
        yield
        rate_limiter.RateLimiter._instance = None
        rate_limiter._default_limiter = None

    def test_min_delay_enforced(self):
        """Vérifie que le délai minimum est respecté."""
        from src.utils.rate_limiter import RateLimiter

        limiter = RateLimiter(min_delay=0.1)

        start = time.time()
        limiter.wait()
        limiter.wait()
        elapsed = time.time() - start

        # Deuxième appel doit attendre au moins min_delay
        assert elapsed >= 0.1

    def test_first_call_no_wait(self):
        """Premier appel ne doit pas attendre."""
        from src.utils.rate_limiter import RateLimiter

        limiter = RateLimiter(min_delay=1.0)

        start = time.time()
        waited = limiter.wait()
        elapsed = time.time() - start

        # Premier appel quasi instantané
        assert elapsed < 0.1
        assert waited < 0.1

    def test_burst_limit(self):
        """Vérifie que le burst limit fonctionne."""
        from src.utils.rate_limiter import RateLimiter

        # Burst de 3 requêtes max dans 1 seconde, sans délai minimum
        limiter = RateLimiter(min_delay=0.0, burst_limit=3, burst_window=1.0)

        # Les 3 premières doivent passer rapidement
        start = time.time()
        for _ in range(3):
            limiter.wait()
        elapsed_burst = time.time() - start

        assert elapsed_burst < 0.2  # 3 requêtes rapides

        # La 4ème doit attendre la fenêtre
        start = time.time()
        limiter.wait()
        elapsed_fourth = time.time() - start

        # Devrait attendre ~1 seconde (fenêtre burst)
        assert elapsed_fourth >= 0.8

    def test_singleton_pattern(self):
        """Vérifie que le singleton fonctionne."""
        from src.utils.rate_limiter import RateLimiter

        limiter1 = RateLimiter(min_delay=0.5)
        limiter2 = RateLimiter(min_delay=1.0)  # Paramètre ignoré

        assert limiter1 is limiter2
        assert limiter1._min_delay == 0.5  # Premier paramètre conservé

    def test_thread_safety(self):
        """Vérifie que le rate limiter est thread-safe."""
        from src.utils.rate_limiter import RateLimiter

        limiter = RateLimiter(min_delay=0.05)
        call_times = []
        lock = threading.Lock()

        def worker():
            limiter.wait()
            with lock:
                call_times.append(time.time())

        threads = [threading.Thread(target=worker) for _ in range(5)]

        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Vérifier que les appels sont espacés
        call_times.sort()
        for i in range(1, len(call_times)):
            gap = call_times[i] - call_times[i-1]
            # Chaque appel doit être espacé d'au moins min_delay (avec tolérance)
            assert gap >= 0.04, f"Gap trop court: {gap}"

    def test_reset(self):
        """Vérifie que reset fonctionne."""
        from src.utils.rate_limiter import RateLimiter

        limiter = RateLimiter(min_delay=0.5)
        limiter.wait()

        # Sans reset, le prochain appel attendrait
        limiter.reset()

        # Après reset, pas d'attente
        start = time.time()
        limiter.wait()
        elapsed = time.time() - start

        assert elapsed < 0.1

    def test_get_rate_limiter_helper(self):
        """Vérifie la fonction helper get_rate_limiter."""
        from src.utils.rate_limiter import get_rate_limiter

        limiter1 = get_rate_limiter(min_delay=0.2)
        limiter2 = get_rate_limiter(min_delay=0.5)  # Ignoré

        assert limiter1 is limiter2
