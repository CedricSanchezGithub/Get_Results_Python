import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException


def navigation(driver, timeout: int = 10):
    """
    Navigue vers la "Journée suivante" en gérant proprement la fin de la pagination.

    - Logue en INFO si la fin est atteinte (bouton désactivé ou non trouvé).
    - Logue en WARNING si le clic est intercepté et qu'un fallback JS est utilisé.
    - Logue en ERROR uniquement pour les erreurs inattendues.

    Args:
        driver : Instance Selenium WebDriver.
        timeout: Délai d'attente pour les éléments.

    Returns:
        bool : True si la navigation a réussi, False si la fin est atteinte ou en cas d'erreur.
    """
    logger = logging.getLogger(__name__)
    button_selector = (By.CSS_SELECTOR, '[title="Journée suivante"]')

    try:
        # 1. Attendre que le bouton soit présent dans le DOM
        #    Ceci nous permet de vérifier son état (ex: 'disabled')
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(button_selector)
        )

        button_to_click = driver.find_element(*button_selector)

        # 2. Vérifier si le bouton est désactivé (Cas de fin normal)
        if button_to_click.get_attribute("disabled"):
            logger.info("Fin de la navigation : Le bouton 'Journée suivante' est désactivé.")
            return False

        # 3. Attendre que le bouton soit cliquable (s'il n'est pas désactivé)
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(button_selector)
        )

        current_url = driver.current_url

        # 4. Tenter de cliquer
        try:
            button_to_click.click()
        except ElementClickInterceptedException:
            # Fallback : Un autre élément (ex: bannière) bloque le clic
            logger.warning("Clic normal intercepté. Tentative de clic via JavaScript.")
            driver.execute_script("arguments[0].click();", button_to_click)

        logger.debug("Changement vers la journée suivante (clic effectué)")

        # 5. Attendre que l'URL change pour confirmer la navigation
        WebDriverWait(driver, timeout).until(EC.url_changes(current_url))

        return True

    except (TimeoutException, NoSuchElementException):
        # Cas de fin normal : Le bouton n'a pas été trouvé dans le délai.
        logger.info("Fin de la navigation : Aucun bouton 'Journée suivante' cliquable trouvé.")
        return False

    except Exception as e:
        # Vraie erreur inattendue
        logger.error(f"Erreur inattendue et majeure lors de la navigation : {e}", exc_info=True)
        return False