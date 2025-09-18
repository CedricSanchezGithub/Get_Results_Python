import logging
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def navigation(driver, timeout: int = 10):
    """
    Navigue sur les pages disponibles. Retourne False lorsqu'il n'y a plus de pages à naviguer.

    Args :
        driver : Instance Selenium WebDriver.

    Returns :
        bool : True si la navigation continue, False si la fin des pages est atteinte.
    """
    try:
        # Attendre que le bouton "Journée suivante" soit présent et cliquable
        button_to_click = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[title="Journée suivante"]'))
        )

        if button_to_click.get_attribute("disabled"):
            logging.getLogger(__name__).info("Le bouton 'Journée suivante' est désactivé. Fin de la navigation.")
            return False

        current_url = driver.current_url
        # Essayer un clic normal d'abord
        try:
            button_to_click.click()
        except Exception:
            # Fallback JS click si nécessaire
            driver.execute_script("arguments[0].click();", button_to_click)
        logging.getLogger(__name__).debug("Changement vers la journée suivante (clic effectué)")

        # Attendre que l'URL change (les URLs contiennent 'journee-<n>/')
        WebDriverWait(driver, timeout).until(EC.url_changes(current_url))
        return True

    except NoSuchElementException:
        logging.getLogger(__name__).info("Aucun autre bouton 'Journée suivante' trouvé. Fin de la navigation.")
        return False

    except Exception as e:
        logging.getLogger(__name__).error(f"Erreur lors de la navigation : {e}")
        return False
