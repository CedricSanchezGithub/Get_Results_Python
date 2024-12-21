import os
import csv
import json
from bs4 import BeautifulSoup

def get_content(driver, folder, html_filename, csv_filename, json_filename, tag_name=None, class_name=None, id_name=None):
    """Récupère le contenu d'une balise ou d'une classe HTML spécifiée et l'enregistre dans un fichier HTML, CSV, et JSON dans un dossier spécifié."""
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(folder):
        os.makedirs(folder)

    html_filepath = os.path.join(folder, html_filename)
    csv_filepath = os.path.join(folder, csv_filename)
    json_filepath = os.path.join(folder, json_filename)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")

    # Recherche de la balise ou classe spécifiée
    if class_name:
        content = soup.find(tag_name, class_=class_name)
    elif tag_name:
        content = soup.find(tag_name)
    elif id_name:
        content = soup.find(id_name)
    else:
        print("Ni balise ni classe spécifiée. Aucun contenu récupéré.")
        return

    if content:
        # Sauvegarde en fichier HTML
        with open(html_filepath, "w", encoding="utf-8") as file:
            file.write(str(content))
        print(f"Contenu de <{tag_name}> sauvegardé dans le fichier : {html_filepath}")

        # Extraction des données et sauvegarde en CSV et JSON
        rows = content.find_all("tr")
        data = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:  # Vérification pour éviter des erreurs
                position = cols[0].text.strip()
                club_name = cols[1].find("span").text.strip() if cols[1].find("span") else cols[1].text.strip()
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
        print(f"Aucune balise <{tag_name}> avec classe '{class_name}' trouvée sur la page.")
