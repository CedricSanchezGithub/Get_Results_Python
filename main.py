import time
from selenium import webdriver
from src.navigation.cookies import cookies
from src.navigation.navigation import navigation
from src.scraper.get_score import save_html_locally, save_tbody_content

driver = webdriver.Chrome()
driver.get("https://www.ffhandball.fr/competitions/saison-2024-2025-20/regional/16-ans-f-territorial-25610/poule-150409/journee-1")

#cookies(driver)
#time.sleep(2)
#navigation(driver)
save_html_locally(driver)
save_tbody_content(driver)