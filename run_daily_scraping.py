import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.scraping.get_all import get_all
from src.utils.purge_data import purge_data
from src.utils.purge.tables_drop.db_drop_option import connection
from src.utils.sources.urls import urls
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display

display = Display(visible=False, size=(1920, 1080))
display.start()

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = "/usr/bin/chromium-browser"

service = Service(executable_path="/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)


def run_daily_scraping():
    start_time = time.time()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        for entry in urls:
            category = entry["category"]
            phase = entry["phase"]
            url = entry["url"]

            try:
                purge_data(category)
            except Exception as e:
                print(f"Erreur lors de la purge des données: {e}")

            try:
                driver.get(url)
                get_all(driver, category)
            except Exception as e:
                print(f"Erreur lors du traitement de {category} - {phase} : {e}")
                continue

    finally:
        connection.close()
        print("Connexion MySQL fermée.")

        driver.quit()
        print("Driver fermé.")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Temps total d'exécution: {elapsed_time:.2f} secondes")