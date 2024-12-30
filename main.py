from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.database.db_drop_option import connection
from src.scraper.get_all import get_all
from src.scraper.get_content import get_content

# Configuration de Chrome en mode headless
chrome_options = Options()
chrome_options.add_argument("--headless")  # Exécute Chrome sans interface graphique
chrome_options.add_argument("--no-sandbox")  # Nécessaire pour Docker
chrome_options.add_argument("--disable-dev-shm-usage")  # Réduit les risques de plantage dans Docker
chrome_options.add_argument("--disable-gpu")  # Optionnel, améliore la compatibilité sur certaines machines
chrome_options.add_argument("--window-size=1920x1080")

# Initialisation du driver avec les options
driver = webdriver.Chrome(options=chrome_options)

# Navigation vers l'URL cible
driver.get("https://www.ffhandball.fr/competitions/saison-2024-2025-20/regional/16-ans-f-territorial-25610/poule-150409/journee-1")

if __name__ == "__main__":
    try:
        get_all(driver)
        # get_content(driver, "tbody")
    finally:
        connection.close()
        print("Connexion MySQL fermée.")

driver.close()



