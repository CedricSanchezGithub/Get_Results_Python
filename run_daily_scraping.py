import time
import logging
from src.saving.db_logger import create_log_entry, update_log_entry
from src.source.api_fetcher import get_urls_from_api
from src.utils.logging_config import configure_logging
from src.scraping.get_all import get_all

def run_daily_scraping():
    # 1. Configuration initiale
    configure_logging()
    logger = logging.getLogger(__name__)

    # 2. Création de l'entrée de log en BDD (Statut: RUNNING)
    log_id = create_log_entry()
    start_time = time.time()
    logger.info("🚀 Job scraping: début (Mode Requests / Sans Headless)")

    job_status = "SUCCESS"
    error_message = None

    try:

        urls_list = get_urls_from_api()

        for entry in urls_list:
            category = entry.get("category")
            target_url = entry.get("url")

            # Validation rapide
            if not category or not target_url:
                logger.warning(f"⚠️ Entrée invalide ignorée : {entry}")
                continue

            try:
                # Appel direct à la logique requests (voir src/scraping/get_all.py)
                get_all(target_url, category)

            except Exception as e:
                # On capture l'erreur pour une catégorie spécifique sans arrêter tout le job
                logger.exception(f"❌ Erreur critique sur la catégorie {category}: {e}")
                job_status = "PARTIAL_SUCCESS"
                # On concatène les erreurs pour le message de fin
                msg = f"Erreur sur {category}: {str(e)}"
                error_message = f"{error_message}; {msg}" if error_message else msg
                continue

    except Exception as e:
        # Erreur fatale qui arrête tout le script (ex: panne BDD globale)
        logger.exception(f"🔥 Erreur fatale globale: {e}")
        job_status = "FAILURE"
        error_message = str(e)

    finally:
        # 4. Calculs de fin et mise à jour du log en BDD
        elapsed_time = time.time() - start_time
        logger.info(f"🏁 Job scraping terminé en {elapsed_time:.2f} s. Statut: {job_status}")

        update_log_entry(
            log_id=log_id,
            status=job_status,
            duration=elapsed_time,
            message=error_message
        )


if __name__ == "__main__":
    run_daily_scraping()