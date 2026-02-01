import pytest
from datetime import datetime, timezone
from src.utils.format_date import format_date


class TestFormatDateISO:
    """Tests pour le parsing de dates ISO 8601."""

    def test_iso_with_timezone(self):
        result = format_date("2025-01-15T14:30:00+01:00")
        assert result is not None
        assert result.tzinfo == timezone.utc
        # 14:30 Paris = 13:30 UTC
        assert result.hour == 13
        assert result.minute == 30

    def test_iso_without_timezone(self):
        result = format_date("2025-01-15T14:30:00")
        assert result is not None
        assert result.tzinfo == timezone.utc

    def test_iso_date_only(self):
        result = format_date("2025-01-15")
        assert result is not None
        # 00:00 Paris = 23:00 UTC la veille (hiver)
        assert result.month == 1
        assert result.year == 2025


class TestFormatDateFrench:
    """Tests pour le parsing de dates en français."""

    def test_french_with_time(self):
        result = format_date("15 janvier 2025 14h30")
        assert result is not None
        assert result.day == 15
        assert result.month == 1
        assert result.year == 2025

    def test_french_without_time(self):
        result = format_date("15 janvier 2025")
        assert result is not None
        # Sans heure = 00:00 Paris = 23:00 UTC la veille
        assert result.month == 1
        assert result.year == 2025

    def test_french_with_accent(self):
        result = format_date("15 février 2025")
        assert result is not None
        assert result.month == 2

    def test_french_without_accent(self):
        result = format_date("15 fevrier 2025")
        assert result is not None
        assert result.month == 2

    def test_french_aout_with_accent(self):
        result = format_date("15 août 2025")
        assert result is not None
        assert result.month == 8

    def test_french_decembre(self):
        result = format_date("25 décembre 2025 20h00")
        assert result is not None
        assert result.month == 12

    def test_french_with_non_breaking_space(self):
        # \xa0 = non-breaking space (courant dans le HTML FFHandball)
        result = format_date("15\xa0janvier\xa02025\xa014h30")
        assert result is not None
        assert result.month == 1


class TestFormatDateEdgeCases:
    """Tests pour les cas limites."""

    def test_none_input(self):
        assert format_date(None) is None

    def test_empty_string(self):
        assert format_date("") is None

    def test_non_disponible(self):
        assert format_date("Date non disponible") is None

    def test_invalid_format(self):
        assert format_date("invalid date string") is None

    def test_unknown_month(self):
        assert format_date("15 badmonth 2025") is None
