import requests
import os

# ==========================================
# 🔧 CONFIGURATION
# Colle ici l'URL précise de la page CLASSEMENT d'une poule
# Exemple : "https://www.ffhandball.fr/competitions/saison-2024-2025/.../poule-123456/classement/"
URL_A_ANALYSER = "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/16-ans-m-preregionale-1ere-division-28343/poule-169284/classements/"


# ==========================================

def save_raw_page(url):
    print(f"🚀 Démarrage du dump pour : {url}")

    # On se fait passer pour un vrai navigateur (Chrome sur Windows)
    # C'est CRITIQUE pour ne pas se faire rejeter par le site
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lève une erreur si 404 ou 500

        filename = "debug_ffhandball_dump.html"

        # On sauvegarde le contenu brut (encodage utf-8 pour ne pas casser les accents)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"✅ SUCCÈS ! Page sauvegardée dans : {filename}")
        print(f"📂 Taille du fichier : {len(response.text)} caractères.")
        print("👉 Envoie-moi ce fichier pour analyse.")

    except Exception as e:
        print(f"❌ ERREUR : Impossible de récupérer la page.")
        print(f"Détail : {e}")


if __name__ == "__main__":
    if "REMPLACE_MOI" in URL_A_ANALYSER:
        print("⚠️  ATTENTION : Tu as oublié de mettre ton URL dans la variable URL_A_ANALYSER ligne 8 !")
    else:
        save_raw_page(URL_A_ANALYSER)