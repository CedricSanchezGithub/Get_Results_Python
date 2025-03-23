import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from trio import sleep

from src.scraping.get_all import get_all
from src.scraping.get_content import get_content
from src.utils.purge.tables_drop.db_drop_option import connection
from src.utils.purge_data import purge_data
from src.utils.sources.urls import urls
from env import is_raspberry_pi

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

def run_daily_scraping():
    start_time = time.time()

    if is_raspberry_pi():
        print("📦 Exécution sur Raspberry Pi")
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        print("💻 Exécution sur environnement de développement")
        driver = webdriver.Chrome(options=chrome_options)

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

    elapsed_time = time.time() - start_time
    print(f"Temps total d'exécution: {elapsed_time:.2f} secondes")


