import os
import csv
from bs4 import BeautifulSoup

def save_match_results(driver, folder, csv_filename, class_name):
    """Récupère les résultats de match à partir d'une classe HTML spécifiée et les enregistre dans un fichier CSV."""

    if not os.path.exists(folder):
        os.makedirs(folder)

    csv_filepath = os.path.join(folder, csv_filename)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")

    if not class_name:
        print("Aucune classe spécifiée. Aucun contenu récupéré.")
        return

    content = soup.find_all(class_=class_name)
    if not content:
        print(f"Aucune balise avec la classe '{class_name}' trouvée.")
        return

    data = []
    for match in content:
        try:
            date_time = match.find("p", class_="block_date__dYMQX").text.strip()
            team_1_name = match.find("div", class_="styles_teamName__aH4Gu styles_left__svLY+").text.strip()
            team_1_score = match.find("div", class_="styles_score__ELPXO styles_winner__LkkrE").text.strip()
            team_2_name = match.find("div", class_="styles_teamName__aH4Gu styles_right__wdfIf").text.strip()
            team_2_score = match.find("div", class_="styles_score__ELPXO").text.strip()
            match_link = match["href"]

            data.append({
                "date_time": date_time,
                "team_1_name": team_1_name,
                "team_1_score": team_1_score,
                "team_2_name": team_2_name,
                "team_2_score": team_2_score,
                "match_link": match_link
            })
        except AttributeError:
            print("Un des éléments de match est manquant, passage au suivant.")
            continue

    with open(csv_filepath, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["date_time", "team_1_name", "team_1_score", "team_2_name", "team_2_score", "match_link"])
        writer.writeheader()
        writer.writerows(data)
    print(f"Données sauvegardées dans le fichier CSV : {csv_filepath}")
