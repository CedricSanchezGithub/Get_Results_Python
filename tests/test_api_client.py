import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from src.saving.api_client import IngestClient
from src.models.models import MatchIngest


@pytest.fixture
def ingest_client():
    """Client d'ingestion avec configuration de test."""
    with patch.dict("os.environ", {
        "BACKEND_API_URL": "http://test-api/ingest",
        "BACKEND_API_KEY": "test-key"
    }):
        return IngestClient(max_retries=3, base_delay=0.01)  # Délai court pour les tests


@pytest.fixture
def sample_matches():
    """Liste de matchs pour les tests."""
    return [
        MatchIngest(
            match_date=datetime(2025, 1, 15, 14, 30, tzinfo=timezone.utc),
            team_1_name="Club A",
            team_1_score=25,
            team_2_name="Club B",
            team_2_score=22,
            category="-18M",
            pool_id="169284"
        )
    ]


class TestIngestClientInit:
    """Tests d'initialisation du client."""

    def test_init_with_env_vars(self, ingest_client):
        assert ingest_client.api_url == "http://test-api/ingest"
        assert ingest_client.api_key == "test-key"
        assert ingest_client.max_retries == 3

    def test_init_without_api_key(self):
        """Vérifie le warning quand api_key est absente."""
        from src.settings import BackendAPISettings
        with patch("src.saving.api_client.get_backend_settings") as mock_settings:
            mock_settings.return_value = BackendAPISettings(
                api_url="http://test",
                api_key=None
            )
            client = IngestClient()
            assert client.api_key is None


class TestIngestClientSendMatches:
    """Tests d'envoi de matchs."""

    def test_send_empty_list(self, ingest_client):
        assert ingest_client.send_matches([]) is True

    def test_send_success(self, ingest_client, sample_matches):
        with patch.object(ingest_client.session, 'post') as mock_post:
            mock_post.return_value = MagicMock(status_code=200)

            result = ingest_client.send_matches(sample_matches)

            assert result is True
            mock_post.assert_called_once()

    def test_send_201_created(self, ingest_client, sample_matches):
        with patch.object(ingest_client.session, 'post') as mock_post:
            mock_post.return_value = MagicMock(status_code=201)

            result = ingest_client.send_matches(sample_matches)

            assert result is True


class TestIngestClientRetry:
    """Tests du mécanisme de retry."""

    def test_no_retry_on_403(self, ingest_client, sample_matches):
        with patch.object(ingest_client.session, 'post') as mock_post:
            mock_post.return_value = MagicMock(status_code=403, text="Forbidden")

            result = ingest_client.send_matches(sample_matches)

            assert result is False
            assert mock_post.call_count == 1  # Pas de retry sur 403

    def test_no_retry_on_400(self, ingest_client, sample_matches):
        with patch.object(ingest_client.session, 'post') as mock_post:
            mock_post.return_value = MagicMock(status_code=400, text="Bad Request")

            result = ingest_client.send_matches(sample_matches)

            assert result is False
            assert mock_post.call_count == 1

    def test_retry_on_500(self, ingest_client, sample_matches):
        with patch.object(ingest_client.session, 'post') as mock_post:
            mock_post.return_value = MagicMock(status_code=500, text="Server Error")

            result = ingest_client.send_matches(sample_matches)

            assert result is False
            assert mock_post.call_count == 3  # 3 tentatives

    def test_retry_on_network_error(self, ingest_client, sample_matches):
        import requests

        with patch.object(ingest_client.session, 'post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

            result = ingest_client.send_matches(sample_matches)

            assert result is False
            assert mock_post.call_count == 3

    def test_retry_then_success(self, ingest_client, sample_matches):
        with patch.object(ingest_client.session, 'post') as mock_post:
            # Échec puis succès
            mock_post.side_effect = [
                MagicMock(status_code=500, text="Error"),
                MagicMock(status_code=200)
            ]

            result = ingest_client.send_matches(sample_matches)

            assert result is True
            assert mock_post.call_count == 2

    def test_jitter_adds_randomness(self, ingest_client, sample_matches):
        """Vérifie que le jitter ajoute de l'aléatoire au délai."""
        import time
        delays = []

        def capture_delay(seconds):
            delays.append(seconds)

        with patch.object(ingest_client.session, 'post') as mock_post, \
             patch('src.saving.api_client.time.sleep', side_effect=capture_delay):
            mock_post.return_value = MagicMock(status_code=500, text="Error")
            ingest_client.send_matches(sample_matches)

        # Avec base_delay=0.01, le delay de base serait 0.01, 0.02
        # Avec jitter (0 à 0.5), les delays doivent être >= base mais < base + 0.5
        assert len(delays) == 2  # 2 retries = 2 sleeps
        assert all(d >= 0.01 for d in delays)
        assert all(d < 0.6 for d in delays)  # base_delay * 2 + max_jitter


class TestIngestClientSendRankings:
    """Tests d'envoi de classements."""

    @pytest.fixture
    def sample_rankings(self):
        """Liste de classements pour les tests."""
        from src.models.models import RankingIngest
        return [
            RankingIngest(
                category="-18M",
                pool_id="169284",
                team_name="Club A",
                rank=1,
                points=15,
                matches_played=5,
                won=5,
                draws=0,
                lost=0
            )
        ]

    def test_send_empty_list(self, ingest_client):
        assert ingest_client.send_rankings([]) is True

    def test_send_rankings_success(self, ingest_client, sample_rankings):
        with patch.object(ingest_client.session, 'post') as mock_post:
            mock_post.return_value = MagicMock(status_code=200)

            result = ingest_client.send_rankings(sample_rankings)

            assert result is True
            mock_post.assert_called_once()

    def test_send_rankings_no_url(self, sample_rankings):
        """Retourne False si aucune URL de rankings configurée."""
        from src.settings import BackendAPISettings, ScraperSettings
        with patch("src.saving.api_client.get_backend_settings") as mock_backend, \
             patch("src.saving.api_client.get_scraper_settings") as mock_scraper:
            mock_backend.return_value = BackendAPISettings(
                api_url=None,
                rankings_api_url=None,
                api_key="test"
            )
            mock_scraper.return_value = ScraperSettings()
            client = IngestClient()

            result = client.send_rankings(sample_rankings)

            assert result is False
