"""
Configuration centralisée avec validation Pydantic.
Charge et valide les variables d'environnement au démarrage.
"""
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Configuration de la base de données MySQL."""

    model_config = SettingsConfigDict(
        env_prefix="MYSQL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    host: str = Field(default="localhost", description="Hôte MySQL")
    port: int = Field(default=3306, description="Port MySQL")
    user: Optional[str] = Field(default=None, description="Utilisateur MySQL")
    password: Optional[str] = Field(default=None, description="Mot de passe MySQL")
    database: Optional[str] = Field(default=None, description="Nom de la base de données")

    @property
    def connection_params(self) -> dict:
        """Retourne les paramètres de connexion pour PyMySQL."""
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.database
        }

    @property
    def is_configured(self) -> bool:
        """Vérifie si la configuration DB est complète."""
        return all([self.user, self.password, self.database])


class BackendAPISettings(BaseSettings):
    """Configuration de l'API backend pour l'ingestion des données."""

    model_config = SettingsConfigDict(
        env_prefix="BACKEND_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    api_url: Optional[str] = Field(
        default=None,
        description="URL de l'endpoint d'ingestion"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="Clé API pour l'authentification"
    )

    @field_validator("api_url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("L'URL doit commencer par http:// ou https://")
        return v


class SourceAPISettings(BaseSettings):
    """Configuration de l'API source pour la liste des compétitions."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Ces champs utilisent les noms exacts des variables d'env (sans préfixe)
    api_url: str = Field(
        default="http://backend:8081/api/competitions",
        validation_alias="API_URL",
        description="URL de l'API des compétitions"
    )
    api_key: str = Field(
        default="secret_local_dev",
        validation_alias="API_KEY",
        description="Clé API"
    )


class ScraperSettings(BaseSettings):
    """Configuration du scraper."""

    model_config = SettingsConfigDict(
        env_prefix="SCRAPER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    max_workers: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Nombre de workers parallèles"
    )
    rate_limit_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Délai minimum entre les requêtes (secondes)"
    )
    request_timeout: int = Field(
        default=15,
        ge=5,
        le=60,
        description="Timeout des requêtes HTTP (secondes)"
    )


class Settings(BaseSettings):
    """Configuration globale de l'application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Sous-configurations (chargées à la demande)
    _db: Optional[DatabaseSettings] = None
    _backend: Optional[BackendAPISettings] = None
    _source_api: Optional[SourceAPISettings] = None
    _scraper: Optional[ScraperSettings] = None

    # Configuration générale
    debug: bool = Field(default=False, description="Mode debug")
    log_level: str = Field(default="INFO", description="Niveau de log")

    @property
    def db(self) -> DatabaseSettings:
        if self._db is None:
            self._db = DatabaseSettings()
        return self._db

    @property
    def backend(self) -> BackendAPISettings:
        if self._backend is None:
            self._backend = BackendAPISettings()
        return self._backend

    @property
    def source_api(self) -> SourceAPISettings:
        if self._source_api is None:
            self._source_api = SourceAPISettings()
        return self._source_api

    @property
    def scraper(self) -> ScraperSettings:
        if self._scraper is None:
            self._scraper = ScraperSettings()
        return self._scraper

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Niveau de log invalide. Valeurs possibles: {valid_levels}")
        return v_upper


@lru_cache()
def get_settings() -> Settings:
    """
    Retourne l'instance singleton des settings.
    Utilise lru_cache pour ne charger qu'une seule fois.
    """
    return Settings()


# Raccourcis pour accès direct
def get_db_settings() -> DatabaseSettings:
    return get_settings().db


def get_backend_settings() -> BackendAPISettings:
    return get_settings().backend


def get_source_api_settings() -> SourceAPISettings:
    return get_settings().source_api


def get_scraper_settings() -> ScraperSettings:
    return get_settings().scraper
