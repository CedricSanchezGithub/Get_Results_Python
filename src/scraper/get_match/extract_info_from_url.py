import os
import csv
import time


def extract_info_from_url(url):
    """
    Extrait les informations de l'URL et les enregistre dans un fichier CSV.
    """
    # Extraire les informations
    competition = get_competition_via_url(url)
    time.sleep(2)
    journee = get_day_via_url(url)

    # Préparer le dossier et le fichier
    folder = "data"
    csv_filename = "day_and_competition.csv"
    os.makedirs(folder, exist_ok=True)
    csv_filepath = os.path.join(folder, csv_filename)

    # Enregistrer dans le CSV
    save_to_csv(csv_filepath, competition, journee)


def get_competition_via_url(url):
    """
    Extrait la compétition de l'URL en découpant la chaîne.
    """
    print("Extracting competition ")
    parts = url.split('/')
    competition = parts[-4]
    return competition


def get_day_via_url(url):
    """
    Extrait la journée de l'URL en découpant la chaîne.
    """
    print("Extracting journee de l'URL ")
    parts = url.split('/')
    journee = parts[-2]
    return journee



def save_to_csv(csv_filepath, competition, journee):
    """
    Enregistre les informations dans un fichier CSV.
    Supprime et recrée le fichier si reset=True.
    """

    if os.path.isfile(csv_filepath):
        os.remove(csv_filepath)
        print(f"Fichier CSV supprimé : {csv_filepath}")

    with open(csv_filepath, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["competition", "journee"])
        writer.writerow([competition, journee])

    print(f"Informations enregistrées : {competition}, {journee} dans {csv_filepath}")
