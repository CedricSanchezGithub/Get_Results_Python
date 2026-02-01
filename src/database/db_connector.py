import time
import pymysql
import sys
import logging

from src.settings import get_db_settings

logger = logging.getLogger(__name__)

# Flag pour éviter de refaire le healthcheck à chaque connexion
_mysql_ready = False


def wait_for_mysql(config: dict, retries: int = 10, delay: int = 3):
    """Attend que MySQL soit prêt à accepter les connexions (appelé une seule fois)."""
    global _mysql_ready

    if _mysql_ready:
        return

    logger.info(f"Vérification de la disponibilité MySQL @ {config['host']}:{config['port']}...")
    for i in range(1, retries + 1):
        try:
            conn = pymysql.connect(**config)
            conn.close()
            logger.info(f"MySQL est prêt (connexion réussie à la tentative {i}).")
            _mysql_ready = True
            return
        except pymysql.err.OperationalError as e:
            logger.warning(f"[{i}/{retries}] MySQL non disponible: {e}")
            if i < retries:
                time.sleep(delay)

    logger.error("Impossible de se connecter à MySQL après plusieurs tentatives.")
    sys.exit(1)


def get_connection():
    """Retourne une connexion MySQL. Le healthcheck n'est fait qu'une seule fois."""
    db_settings = get_db_settings()

    if not db_settings.is_configured:
        raise RuntimeError(
            "Variables d'environnement manquantes pour MySQL: "
            "MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE. "
            "Vérifiez votre fichier .env ou les variables du conteneur."
        )

    config = db_settings.connection_params

    # Healthcheck initial (skip si déjà validé)
    wait_for_mysql(config)

    return pymysql.connect(**config)