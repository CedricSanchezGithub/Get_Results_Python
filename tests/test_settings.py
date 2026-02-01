import pytest
from unittest.mock import patch
from pydantic import ValidationError


class TestDatabaseSettings:
    """Tests pour la configuration base de données."""

    def test_default_host_and_port(self):
        """Vérifie les valeurs par défaut pour host et port."""
        from src.settings import DatabaseSettings
        # On ne teste que les defaults qui ne viennent pas de .env
        settings = DatabaseSettings(_env_file=None)

        assert settings.host == "localhost"
        assert settings.port == 3306

    def test_is_configured_false_without_credentials(self):
        """Vérifie que is_configured est False sans credentials."""
        from src.settings import DatabaseSettings
        settings = DatabaseSettings(user=None, password=None, database=None, _env_file=None)

        assert settings.is_configured is False

    def test_from_env(self):
        env = {
            "MYSQL_HOST": "db.example.com",
            "MYSQL_PORT": "3307",
            "MYSQL_USER": "testuser",
            "MYSQL_PASSWORD": "testpass",
            "MYSQL_DATABASE": "testdb"
        }
        with patch.dict("os.environ", env, clear=True):
            from src.settings import DatabaseSettings
            settings = DatabaseSettings()

            assert settings.host == "db.example.com"
            assert settings.port == 3307
            assert settings.user == "testuser"
            assert settings.is_configured is True

    def test_connection_params(self):
        env = {
            "MYSQL_HOST": "localhost",
            "MYSQL_USER": "user",
            "MYSQL_PASSWORD": "pass",
            "MYSQL_DATABASE": "db"
        }
        with patch.dict("os.environ", env, clear=True):
            from src.settings import DatabaseSettings
            settings = DatabaseSettings()
            params = settings.connection_params

            assert params["host"] == "localhost"
            assert params["user"] == "user"
            assert params["password"] == "pass"
            assert params["database"] == "db"


class TestBackendAPISettings:
    """Tests pour la configuration de l'API backend."""

    def test_default_values_without_env_file(self):
        """Vérifie les valeurs par défaut sans fichier .env."""
        from src.settings import BackendAPISettings
        settings = BackendAPISettings(_env_file=None)

        assert settings.api_url is None
        assert settings.api_key is None

    def test_from_env(self):
        env = {
            "BACKEND_API_URL": "https://api.example.com/ingest",
            "BACKEND_API_KEY": "secret123"
        }
        with patch.dict("os.environ", env, clear=True):
            from src.settings import BackendAPISettings
            settings = BackendAPISettings()

            assert settings.api_url == "https://api.example.com/ingest"
            assert settings.api_key == "secret123"

    def test_url_validation_invalid(self):
        env = {"BACKEND_API_URL": "not-a-url"}
        with patch.dict("os.environ", env, clear=True):
            from src.settings import BackendAPISettings
            with pytest.raises(ValidationError) as exc_info:
                BackendAPISettings()
            assert "http://" in str(exc_info.value)


class TestScraperSettings:
    """Tests pour la configuration du scraper."""

    def test_default_values(self):
        with patch.dict("os.environ", {}, clear=True):
            from src.settings import ScraperSettings
            settings = ScraperSettings()

            assert settings.max_workers == 3
            assert settings.rate_limit_delay == 1.0
            assert settings.request_timeout == 15

    def test_from_env(self):
        env = {
            "SCRAPER_MAX_WORKERS": "5",
            "SCRAPER_RATE_LIMIT_DELAY": "2.5",
            "SCRAPER_REQUEST_TIMEOUT": "30"
        }
        with patch.dict("os.environ", env, clear=True):
            from src.settings import ScraperSettings
            settings = ScraperSettings()

            assert settings.max_workers == 5
            assert settings.rate_limit_delay == 2.5
            assert settings.request_timeout == 30

    def test_max_workers_bounds(self):
        # Trop bas
        with patch.dict("os.environ", {"SCRAPER_MAX_WORKERS": "0"}, clear=True):
            from src.settings import ScraperSettings
            with pytest.raises(ValidationError):
                ScraperSettings()

        # Trop haut
        with patch.dict("os.environ", {"SCRAPER_MAX_WORKERS": "100"}, clear=True):
            from src.settings import ScraperSettings
            with pytest.raises(ValidationError):
                ScraperSettings()


class TestSettings:
    """Tests pour la configuration globale."""

    def test_log_level_validation(self):
        with patch.dict("os.environ", {"LOG_LEVEL": "INVALID"}, clear=True):
            from src.settings import Settings
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            assert "Niveau de log invalide" in str(exc_info.value)

    def test_log_level_case_insensitive(self):
        with patch.dict("os.environ", {"LOG_LEVEL": "debug"}, clear=True):
            from src.settings import Settings
            settings = Settings()
            assert settings.log_level == "DEBUG"

    def test_sub_settings_access(self):
        env = {
            "MYSQL_USER": "user",
            "MYSQL_PASSWORD": "pass",
            "MYSQL_DATABASE": "db"
        }
        with patch.dict("os.environ", env, clear=True):
            from src.settings import Settings
            settings = Settings()

            # Accès aux sous-configurations
            assert settings.db.user == "user"
            assert settings.scraper.max_workers == 3
