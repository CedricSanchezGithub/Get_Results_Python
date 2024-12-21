import time

from src.database.db_drop_option import connection
from src.database.db_writer import db_writer_results
from src.navigation.cookies import cookies
from src.navigation.navigation import navigation
from src.scraper.get_match_results import get_match_results
from src.scraper.get_rank import get_rank


def end_of_navigation():
    """Callback appelé à la fin de la navigation."""
    print("Navigation terminée. Fin des pages atteinte.")

def get_all(driver):
    """
    Gère le processus complet : cookies, classement, navigation et récupération des résultats.
    """
    i = 1
    time.sleep(2)
    cookies(driver)
    get_rank(driver, is_csv=True)

    while True:

        get_match_results(driver)
        db_writer_results()
        i += 1
        print(f"Page {i}")
        # Passe à la journée suivante et vérifie s'il reste des pages
        if not navigation(driver):
            print("Toutes les journées ont été traitées.")
            break
