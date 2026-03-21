import pytest
from datetime import datetime, timezone
from unittest.mock import patch


@pytest.fixture
def mock_urls_from_api():
    """Mock de get_urls_from_api() avec URLs valides."""
    valid_urls = [
        {
            "id": "1",
            "category": "SF",
            "url": "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/16-ans-f-prenationale-28365/poule-169120/journee-1/",
        },
        {
            "id": "2",
            "category": "SG",
            "url": "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/16-ans-m-preregionale-1ere-division-28343/poule-169284/journee-1/",
        },
    ]
    with patch("run_daily_scraping.get_urls_from_api") as mock:
        mock.return_value = valid_urls
        yield mock


@pytest.fixture
def mock_db_logger():
    """Mock des fonctions db_logger pour éviter accès DB."""
    with (
        patch("run_daily_scraping.create_log_entry") as mock_create,
        patch("run_daily_scraping.update_log_entry") as mock_update,
    ):
        mock_create.return_value = 1
        yield {"create": mock_create, "update": mock_update}


@pytest.fixture
def sample_match_data():
    """Données de match valides pour les tests."""
    return {
        "match_date": datetime(2025, 1, 15, 14, 30, tzinfo=timezone.utc),
        "team_1_name": "Club A",
        "team_1_score": 25,
        "team_2_name": "Club B",
        "team_2_score": 22,
        "category": "-18M",
        "pool_id": "169284",
        "official_phase_name": "Excellence",
        "round": "5",
    }


@pytest.fixture
def sample_match_data_minimal():
    """Données de match minimales (sans scores, sans noms d'équipes)."""
    return {
        "match_date": datetime(2025, 1, 15, 14, 30, tzinfo=timezone.utc),
        "team_1_name": "Club A",
        "team_2_name": "Club B",
        "category": "-18M",
        "pool_id": "169284",
    }
