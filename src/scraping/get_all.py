import time

from src.navigation.cookies import cookies
from src.navigation.navigation import navigation
from src.saving.db_writer import db_writer_results
from src.scraping.get_match_results import get_pool_results
from src.utils.purge.csv_drop.purge_csv import purge_csv
from src.utils.purge_data import purge_pool_data


import logging

def end_of_navigation():
    """Callback appelé à la fin de la navigation."""
    logging.getLogger(__name__).info("Navigation terminée. Fin des pages atteinte.")


def get_all(driver, category):
    logging.getLogger(__name__).info(f"Purge du CSV pour la catégorie '{category}'...")

    purge_csv(category)
    purge_pool_data(category)

    time.sleep(2)
    cookies(driver)

    page_count = 1
    while True:
        logging.getLogger(__name__).info(f"Scraping page {page_count} pour la catégorie '{category}'")
        get_pool_results(driver, category)
        page_count += 1
        if not navigation(driver):
            logging.getLogger(__name__).info("Toutes les journées ont été traitées.")
            break

    db_writer_results(category)