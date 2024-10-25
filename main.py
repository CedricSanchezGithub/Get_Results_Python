import time
from selenium import webdriver
from src.cookies import cookies
from src.navigation import navigation

driver = webdriver.Chrome()
driver.get("https://www.ffhandball.fr/competitions/saison-2024-2025-20/regional/16-ans-f-territorial-25610/poule-150409/journee-1")

cookies(driver)
time.sleep(2)
navigation(driver)

# LUNEL MARSILLARGUES HB
# Agree and close

# multiplication_dimension(dimension_input)
# import requests
# import os
# import selenium
#
# URL = "https://www.belex.sites.be.ch/app/fr/systematic/texts_of_law"
#
# response = requests.get(URL)
#
#
# if os.path.exists("data.txt"):
#     os.remove("data.txt")
#     print("Le fichier data.txt a été supprimé.")
#     with open("data.txt", "x") as new_file_create:
#         new_file_create.write(response.content.decode("utf-8"))
#     print(f"Le fichier data.txt a été créé: ")
# else:
#     with open("data.txt", "x") as new_file_create:
#         new_file_create.write(response.content.decode("utf-8"))
#     print(f"Le fichier data.txt a été créé: ")
#
#
# with open("data.txt", "r") as new_file_read:
#     print(new_file_read.read())
