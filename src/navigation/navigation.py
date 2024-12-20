import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def navigation(driver):
    while True:
        try:
            button_to_click = driver.find_element(By.CSS_SELECTOR, '[title="Journée suivante"]')

            if button_to_click.get_attribute("disabled"):
                print("Le bouton 'Journée suivante' est désactivé.")
                break

            button_to_click.click()
            print("Changement vers la journée suivante.")
            time.sleep(2)

        except NoSuchElementException:
            print("Aucun autre bouton 'Journée suivante' trouvé.")
            break
