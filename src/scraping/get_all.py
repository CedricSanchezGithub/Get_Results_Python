import time

from src.navigation.cookies import cookies
from src.navigation.navigation import navigation
from src.saving.db_writer import db_writer_results
from src.scraping.get_match_results import get_pool_results
from src.utils.purge_data import purge_pool_data
import logging


def end_of_navigation():
    """Callback appelé à la fin de la navigation."""
    logging.getLogger(__name__).info("Navigation terminée. Fin des pages atteinte.")


def get_all(driver, category):
    logging.getLogger(__name__).info(f"Purge de la BDD pour la catégorie '{category}'...")
    purge_pool_data(category)

    time.sleep(2)
    cookies(driver)

    page_count = 1
    all_match_data = []

    while True:
        logging.getLogger(__name__).info(f"Scraping page {page_count} pour la catégorie '{category}'")
        page_data = get_pool_results(driver, category)

        if page_data:
            all_match_data.extend(page_data)
            logging.getLogger(__name__).info(f"Page {page_count}: {len(page_data)} matches trouvés.")
        else:
            logging.getLogger(__name__).warning(f"Page {page_count}: Aucun match trouvé.")

        page_count += 1
        if not navigation(driver):
            logging.getLogger(__name__).info("Toutes les journées ont été traitées.")
            break

    logging.getLogger(__name__).info(f"Total de {len(all_match_data)} matches scrapés. Écriture en base de données...")
    db_writer_results(all_match_data, category)