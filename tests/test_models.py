import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from src.models.models import MatchIngest


class TestMatchIngestValidation:
    """Tests de validation du modèle MatchIngest."""

    def test_valid_complete_match(self, sample_match_data):
        match = MatchIngest(**sample_match_data)
        assert match.team_1_name == "Club A"
        assert match.team_1_score == 25
        assert match.official_phase_name == "Excellence"

    def test_valid_minimal_match(self, sample_match_data_minimal):
        match = MatchIngest(**sample_match_data_minimal)
        assert match.team_1_score is None
        assert match.team_2_score is None
        assert match.official_phase_name is None

    def test_missing_required_field(self):
        with pytest.raises(ValidationError):
            MatchIngest(
                match_date=datetime.now(timezone.utc),
                team_1_name="Club A",
                # team_2_name manquant
                category="-18M",
                pool_id="123"
            )

    def test_missing_category(self):
        with pytest.raises(ValidationError):
            MatchIngest(
                match_date=datetime.now(timezone.utc),
                team_1_name="Club A",
                team_2_name="Club B",
                pool_id="123"
                # category manquant
            )


class TestMatchIngestSerialization:
    """Tests de sérialisation JSON."""

    def test_model_dump_json(self, sample_match_data):
        match = MatchIngest(**sample_match_data)
        dumped = match.model_dump(mode='json')

        assert isinstance(dumped, dict)
        assert dumped["team_1_name"] == "Club A"
        assert dumped["team_1_score"] == 25
        assert "match_date" in dumped

    def test_model_dump_excludes_none(self, sample_match_data_minimal):
        match = MatchIngest(**sample_match_data_minimal)
        dumped = match.model_dump(mode='json', exclude_none=True)

        assert "team_1_score" not in dumped
        assert "official_phase_name" not in dumped
