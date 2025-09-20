import time
import logging
from src.utils.logging_config import configure_logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from trio import sleep

from src.scraping.get_all import get_all
from src.scraping.get_content import get_content
from src.utils.purge_data import purge_data
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
    start_time = time.time()
    logger.info("Job scraping: début")

    if is_raspberry_pi():
        logger.info("Environnement: Raspberry Pi (ARM64)")
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        logger.info("Environnement: développement")
        driver = webdriver.Chrome(options=chrome_options)

    try:
        for entry in urls:
            category = entry["category"]
            phase = entry["phase"]
            url = entry["url"]

            try:
                purge_data(category)
                logger.info(f"Purge des données pour la poule '{category}' effectuée")
            except Exception as e:
                logger.error(f"Erreur lors de la purge des données (category={category}): {e}")

            try:
                logger.info(f"Début scraping category={category}, phase={phase}, url={url}")
                driver.get(url)
                get_all(driver, category)
                logger.info(f"Fin scraping category={category}, phase={phase}")
            except Exception as e:
                logger.exception(f"Erreur lors du traitement category={category}, phase={phase}, url={url}: {e}")
                continue

    finally:
        driver.quit()
        logger.info("Driver fermé.")

    elapsed_time = time.time() - start_time
    logger.info(f"Job scraping: fin — durée totale {elapsed_time:.2f} s")
