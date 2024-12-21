import os

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