import os
import time
import pymysql
import sys
from flask.cli import load_dotenv


def wait_for_mysql(host, user, password, db, port=3306, retries=10, delay=3):
    """Attend que MySQL soit prêt à accepter les connexions."""
    print(f"🔍 Tentative de connexion à MySQL @ {host}:{port}...")
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
            print(f"✅ MySQL est prêt (connexion réussie à la tentative {i}).")
            return
        except pymysql.err.OperationalError as e:
            print(f"⏳ [{i}/{retries}] MySQL non dispo : {e}")
            time.sleep(delay)

    print("❌ ERREUR : Impossible de se connecter à MySQL après plusieurs tentatives.")
    sys.exit(1)


def get_connection():
    load_dotenv()

    host = os.getenv("MYSQL_HOST", "localhost")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    database = os.getenv("MYSQL_DATABASE")
    port = int(os.getenv("MYSQL_PORT", 3306))

    # Attendre que MySQL soit opérationnel
    wait_for_mysql(host, user, password, database, port=port)

    # Connexion réelle
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )

# def get_connection():
#     """Crée et retourne une connexion à la base de données."""
#     connection = pymysql.connect(
#         host='mysql_getresults',
#         user='root',
#         password='root',
#         database='getresults'
#     )
#     return connection