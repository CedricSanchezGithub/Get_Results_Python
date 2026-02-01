import pytest
from datetime import datetime, timezone


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
        "round": "5"
    }


@pytest.fixture
def sample_match_data_minimal():
    """Données de match minimales (sans scores)."""
    return {
        "match_date": datetime(2025, 1, 15, 14, 30, tzinfo=timezone.utc),
        "team_1_name": "Club A",
        "team_2_name": "Club B",
        "category": "-18M",
        "pool_id": "169284"
    }
