from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from src.database.db_writer import db_writer_results
from src.scraper.get_content import get_content
from src.scraper.get_match_results import save_match_results

# Configuration de Chrome en mode headless
chrome_options = Options()
chrome_options.add_argument("--headless")  # Exécute Chrome sans interface graphique
chrome_options.add_argument("--no-sandbox")  # Nécessaire pour Docker
chrome_options.add_argument("--disable-dev-shm-usage")  # Réduit les risques de plantage dans Docker
chrome_options.add_argument("--disable-gpu")  # Optionnel, améliore la compatibilité sur certaines machines
chrome_options.add_argument("--window-size=1920x1080")  # Définit une taille d'écran virtuelle

# Initialisation du driver avec les options
driver = webdriver.Chrome(options=chrome_options)

# Navigation vers l'URL cible
driver.get("https://www.ffhandball.fr/competitions/saison-2024-2025-20/regional/16-ans-f-territorial-25610/poule-150409/journee-1")

#cookies(driver)
#time.sleep(2)
#navigation(driver)



save_match_results(
    driver,
    folder="data",
    csv_filename="results.csv",
    class_name="styles_rencontre__9O0P0"
)

db_writer_results()

# Fermeture du driver
driver.close()

