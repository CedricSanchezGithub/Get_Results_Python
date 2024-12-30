import time

from selenium.webdriver.common.by import By

def cookies(driver):
    button_accepte_cookies = driver.find_elements(By.ID, "didomi-notice-agree-button")
    if button_accepte_cookies:
        time.sleep(3)
        button_accepte_cookies[0].click()
    else:
        print("Bannière de cookies inexistante.")
