from selenium import webdriver

from src.scraper.get_content import get_content

driver = webdriver.Chrome()
driver.get("https://www.ffhandball.fr/competitions/saison-2024-2025-20/regional/16-ans-f-territorial-25610/poule-150409/journee-1")

#cookies(driver)
#time.sleep(2)
#navigation(driver)
get_content(driver, folder="data", html_filename="newContent.html", csv_filename="newContent.csv", json_filename="newContent.json", tag_name="html")

driver.close()