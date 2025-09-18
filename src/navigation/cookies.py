import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def cookies(driver, timeout: int = 10):
    """Accepte la bannière cookies si présente, en attendant le bouton cliquable."""
    try:
        # Attendre que le bouton soit présent et cliquable
        button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        button.click()
        return True
    except TimeoutException:
        # Aucun bouton de cookies visible/cliquable dans le délai imparti
        logging.getLogger(__name__).info("Bannière de cookies inexistante ou déjà acceptée.")
        return False
    except Exception as e:
        # Fallback: essayer un clic JS si quelque chose bloque le clic natif
        try:
            elements = driver.find_elements(By.ID, "didomi-notice-agree-button")
            if elements:
                driver.execute_script("arguments[0].click();", elements[0])
                return True
        except Exception:
            pass
        logging.getLogger(__name__).warning(f"Impossible de cliquer sur la bannière de cookies: {e}")
        return False
