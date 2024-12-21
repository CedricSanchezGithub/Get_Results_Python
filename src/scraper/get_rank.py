import os
import csv
import json
from bs4 import BeautifulSoup

def save_html_locally(driver, folder="data", filename="page.html"):
    """Récupère le contenu HTML actuel de la page et l'enregistre dans un fichier dans un dossier spécifié."""
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(folder):
        os.makedirs(folder)

    filepath = os.path.join(folder, filename)
    html_content = driver.page_source
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(html_content)
    print(f"Page HTML sauvegardée dans le fichier : {filepath}")

def save_tbody_content(driver, folder="data", html_filename="tbody_content.html", csv_filename="results.csv", json_filename="results.json"):
    """Récupère le contenu de la balise <tbody> et l'enregistre dans un fichier HTML, CSV, et JSON dans un dossier spécifié."""
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(folder):
        os.makedirs(folder)

    html_filepath = os.path.join(folder, html_filename)
    csv_filepath = os.path.join(folder, csv_filename)
    json_filepath = os.path.join(folder, json_filename)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    tbody_content = soup.find("tbody")

    if tbody_content:
        # Sauvegarde en fichier HTML
        with open(html_filepath, "w", encoding="utf-8") as file:
            file.write(str(tbody_content))
        print(f"Contenu de <tbody> sauvegardé dans le fichier : {html_filepath}")

        # Extraction des données et sauvegarde en CSV et JSON
        rows = tbody_content.find_all("tr")
        data = []

        for row in rows:
            cols = row.find_all("td")
            position = cols[0].text.strip()
            club_name = cols[1].find("span").text.strip()
            points = cols[2].text.strip()
            data.append({"position": position, "club_name": club_name, "points": points})

        # Sauvegarde en CSV
        with open(csv_filepath, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["position", "club_name", "points"])
            writer.writeheader()
            writer.writerows(data)
        print(f"Données sauvegardées dans le fichier CSV : {csv_filepath}")

        # Sauvegarde en JSON
        with open(json_filepath, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Données sauvegardées dans le fichier JSON : {json_filepath}")
    else:
        print("Aucune balise <tbody> trouvée sur la page.")
