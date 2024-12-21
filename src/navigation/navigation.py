import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By


def navigation(driver):
    """
    Navigue sur les pages disponibles. Retourne False lorsqu'il n'y a plus de pages à naviguer.

    Args :
        driver : Instance Selenium WebDriver.

    Returns :
        bool : True si la navigation continue, False si la fin des pages est atteinte.
    """
    try:
        button_to_click = driver.find_element(By.CSS_SELECTOR, '[title="Journée suivante"]')

        if button_to_click.get_attribute("disabled"):
            print("Le bouton 'Journée suivante' est désactivé. Fin de la navigation.")
            return False

        # Utiliser JavaScript pour cliquer sur le bouton
        driver.execute_script("arguments[0].click();", button_to_click)
        print("Changement vers la journée suivante.")
        time.sleep(2)  # Attendre pour laisser la page se charger
        return True

    except NoSuchElementException:
        print("Aucun autre bouton 'Journée suivante' trouvé. Fin de la navigation.")
        return False

    except Exception as e:
        print(f"Erreur lors de la navigation : {e}")
        return False
