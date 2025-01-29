import time

from src.navigation.cookies import cookies
from src.navigation.navigation import navigation
from src.saving.db_writer import db_writer_results
from src.scraping.get_match_results import get_pool_results
from src.utils.purge.tables_drop.db_drop import create_table


def end_of_navigation():
    """Callback appelé à la fin de la navigation."""
    print("Navigation terminée. Fin des pages atteinte.")

def get_all(driver, category):
    """
    Gère le processus complet : cookies, classement, navigation et récupération des résultats.
    """

    i = 1
    time.sleep(2)
    cookies(driver)
    # get_rank(driver, is_csv=True)
    # db_writer_ranking(category)

    while True:
        get_pool_results(driver, category)
        i += 1
        print(f"Page {i}")
        if not navigation(driver):
            print("Toutes les journées ont été traitées.")
            break
    create_table(f"pool_{category}")
    db_writer_results(category)
