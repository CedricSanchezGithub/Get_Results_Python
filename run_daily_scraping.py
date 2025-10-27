import time
import logging
from src.saving.db_logger import create_log_entry, update_log_entry
from src.utils.logging_config import configure_logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from src.scraping.get_all import get_all
from src.utils.purge_data import purge_pool_data
from src.utils.sources.urls import urls
from env import is_raspberry_pi

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")


def run_daily_scraping():
    configure_logging()
    logger = logging.getLogger(__name__)

    log_id = create_log_entry()

    start_time = time.time()
    logger.info("Job scraping: début")

    driver = None
    job_status = "SUCCESS"
    error_message = None

    try:
        if is_raspberry_pi():
            logger.info("Environnement: Raspberry Pi (ARM64)")
            service = Service("/usr/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            logger.info("Environnement: développement")
            driver = webdriver.Chrome(options=chrome_options)

        for entry in urls:
            category = entry["category"]
            try:
                logger.info(f"Début scraping category={category}...")
                driver.get(entry["url"])
                get_all(driver, category)
                logger.info(f"Fin scraping category={category}")
            except Exception as e:
                logger.exception(f"Erreur lors du traitement de la category={category}: {e}")
                job_status = "PARTIAL_SUCCESS"
                error_message = f"Failed on category {category}: {e}"
                continue

    except Exception as e:
        logger.exception(f"Erreur fatale dans le job de scraping: {e}")
        job_status = "FAILURE"
        error_message = str(e)

    finally:
        if driver:
            driver.quit()
            logger.info("Driver fermé.")

        elapsed_time = time.time() - start_time
        logger.info(f"Job scraping: fin — durée totale {elapsed_time:.2f} s")

        update_log_entry(
            log_id=log_id,
            status=job_status,
            duration=elapsed_time,
            message=error_message
        )