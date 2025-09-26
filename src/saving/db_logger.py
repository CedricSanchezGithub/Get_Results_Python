# Fichier : src/saving/db_logger.py
import logging
from datetime import datetime
from src.database.db_connector import get_connection

def create_log_entry() -> int:
    """
    Crée une entrée de log au début d'un job avec le statut 'RUNNING'.
    Retourne l'ID de l'entrée de log créée.
    """
    sql = "INSERT INTO scraping_log (started_at, status) VALUES (%s, 'RUNNING')"
    conn = get_connection()
    log_id = None
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (datetime.now(),))
            log_id = cursor.lastrowid  # Récupère l'ID de la ligne insérée
        conn.commit()
        logging.getLogger(__name__).info(f"Created log entry with ID: {log_id}")
        return log_id
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to create log entry: {e}")
        # On ne veut pas bloquer le job principal si le logging échoue
        return -1
    finally:
        if conn:
            conn.close()

def update_log_entry(log_id: int, status: str, duration: float, message: str = None):
    """
    Met à jour une entrée de log existante avec le statut final et les métriques.
    """
    if log_id is None or log_id < 0:
        logging.getLogger(__name__).warning("Invalid log_id, skipping log update.")
        return

    sql = """
    UPDATE scraping_log 
    SET finished_at = %s, status = %s, duration_seconds = %s, message = %s
    WHERE id = %s
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (datetime.now(), status, duration, message, log_id))
        conn.commit()
        logging.getLogger(__name__).info(f"Updated log entry {log_id} with status: {status}")
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to update log entry {log_id}: {e}")
    finally:
        if conn:
            conn.close()