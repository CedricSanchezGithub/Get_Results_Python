import os
import time
import pymysql
import sys
import logging
from flask.cli import load_dotenv


def wait_for_mysql(host, user, password, db, port, retries=10, delay=3):
    """Attend que MySQL soit prêt à accepter les connexions."""
    logger = logging.getLogger(__name__)
    logger.info(f"Tentative de connexion à MySQL @ {host}:{port}...")
    for i in range(1, retries + 1):
        try:
            conn = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=db,
                port=port
            )
            conn.close()
            logger.info(f"MySQL est prêt (connexion réussie à la tentative {i}).")
            return
        except pymysql.err.OperationalError as e:
            logger.warning(f"[{i}/{retries}] MySQL non disponible: {e}")
            time.sleep(delay)

    logger.error("Impossible de se connecter à MySQL après plusieurs tentatives.")
    sys.exit(1)


def get_connection():
    load_dotenv()

    host = os.getenv("MYSQL_HOST", "localhost")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DATABASE")
    port = int(os.getenv("MYSQL_PORT", "3306"))

    if not all([user, password, database]):
        raise RuntimeError("Variables d'environnement manquantes pour MySQL: MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE. Vérifiez votre fichier .env ou les variables du conteneur.")

    # Attendre que MySQL soit opérationnel
    wait_for_mysql(host, user, password, database, port)

    # Connexion réelle
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )