import logging
from src.utils.purge.csv_drop.purge_csv import purge_csv
from src.database.db_connector import get_connection
from src.utils.purge.tables_drop.db_drop import truncate_table


def purge_data(category):
    purge_csv(category)
    truncate_table(f"pool_{category}")

def purge_pool_data(pool_id):
    """
    Supprime les anciens résultats pour une poule spécifique de la table 'matches'.
    Laisse remonter les exceptions SQL pour que l'appelant puisse annuler le job.
    """
    sql = "DELETE FROM matches WHERE pool_id = %s"
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, (pool_id,))
            connection.commit()
            logging.getLogger(__name__).info(f"Données purgées pour la poule '{pool_id}' dans la table 'matches'.")
    except Exception as e:
        logging.getLogger(__name__).error(f"Erreur lors de la purge pour la poule '{pool_id}': {e}")
        raise
    finally:
        connection.close()