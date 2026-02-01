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
                api_key=None,
                _env_file=None
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
