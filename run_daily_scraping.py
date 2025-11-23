import time
import logging
from src.saving.db_logger import create_log_entry, update_log_entry
from src.utils.logging_config import configure_logging
# Plus d'import Selenium !
from src.scraping.get_all import get_all
from src.utils.sources.urls import urls


# from env import is_raspberry_pi (Devenu inutile pour Selenium, mais peut servir ailleurs)

def run_daily_scraping():
    configure_logging()
    logger = logging.getLogger(__name__)

    log_id = create_log_entry()
    start_time = time.time()
    logger.info("Job scraping (Mode Requests): début")

    job_status = "SUCCESS"
    error_message = None

    try:
        # Plus de détection Raspberry Pi ni de Driver Chrome

        # Boucle principale
        for entry in urls:
            category = entry["category"]
            target_url = entry["url"]

            try:
                get_all(target_url, category)
            except Exception as e:
                logger.exception(f"Erreur critique sur la catégorie {category}: {e}")
                job_status = "PARTIAL_SUCCESS"
                error_message = f"Erreur sur {category}"
                continue

    except Exception as e:
        logger.exception(f"Erreur fatale globale: {e}")
        job_status = "FAILURE"
        error_message = str(e)

    finally:
        elapsed_time = time.time() - start_time
        logger.info(f"Job scraping terminé en {elapsed_time:.2f} s. Statut: {job_status}")

        update_log_entry(
            log_id=log_id,
            status=job_status,
            duration=elapsed_time,
            message=error_message
        )


if __name__ == "__main__":
    run_daily_scraping()