import base64
import json
import logging
import re
import sys
import os
import warnings
from urllib.parse import urlencode

# --- DÉPENDANCES ---
try:
    import requests
    from bs4 import BeautifulSoup
    from urllib3.exceptions import NotOpenSSLWarning

    # On fait taire le warning SSL inutile sur Mac
    warnings.simplefilter('ignore', NotOpenSSLWarning)
except ImportError:
    print("Erreur: Il manque des librairies. Lance: pip install requests beautifulsoup4")
    sys.exit(1)

# --- CONFIGURATION ---
OUTPUT_DIR = "debug_logos_output"
LOGO_SIZE = "64"  # Options: "64", "200", "original"
FFHB_LOGO_CDN = "https://media-logos-clubs.ffhandball.fr"

# --- LISTE DES URLS CIBLES (Mise à jour : journee-1 -> classements) ---
TARGET_URLS = [
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/18-ans-f-2e-division-28369/poule-179943/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/18-ans-m-2e-division-28349/poule-179961/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/18-ans-m-4e-division-28351/poule-179229/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/15-ans-f-1ere-division-28372/poule-179933/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/15-ans-f-3e-division-28374/poule-179253/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/15-ans-m-2e-division-28355/poule-179948/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/15-ans-m-4e-division-28357/poule-179261/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/13-ans-feminin-29209/poule-181331/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-13-feminins-28964/poule-181647/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-13-masculins-28913/poule-181650/classements/",
    # URL sans poule (sera ignorée par le script)
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-13-masculins-28913/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-11-masculins-28912/poule-181640/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-11-masculins-28912/poule-175315/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-13-masculins-28913/poule-175328/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-13-masculins-28913/poule-172095/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/15-ans-m-3e-division-28356/poule-172527/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/15-ans-m-2e-division-28355/poule-169153/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/18-ans-m-2e-division-28349/poule-169141/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/18-ans-m-3e-division-28350/poule-172487/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/16-ans-m-preregionale-1ere-division-28343/poule-169284/classements/",
    # URLs sans poule (seront ignorées)
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-11-feminins-28963/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/coupe-de-l-herault-13-f-29043/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-13-feminins-28964/classements/",

    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/15-ans-f-2e-division-28373/poule-172423/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/15-ans-f-1ere-division-28372/poule-169159/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/18-ans-f-2e-division-28369/poule-172464/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/coupe-de-france/coupe-de-france-regionale-feminine-2025-26-29113/poule-173664/classements/",
    "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/16-ans-f-prenationale-28365/poule-169120/classements/"
]

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("BATCH_LOGOS")


# --- FONCTIONS UTILITAIRES ---

def sanitize_url(url: str) -> str:
    """
    Nettoie l'URL pour faciliter le scraping.
    Si une poule est détectée, on retourne la racine de la poule pour éviter les erreurs de blocs.
    """
    match = re.search(r'(.*?/poule-\d+/)', url)
    if match:
        return match.group(1)
    return url


def xor_decipher(payload, key: str) -> str:
    if isinstance(payload, dict):
        # Ignore l'affichage de l'erreur si c'est juste un 400 attendu (ex: block non trouvé)
        return ""
    if not isinstance(payload, str):
        return ""

    try:
        decoded_bytes = base64.b64decode(payload)
        key_len = len(key)
        key_bytes = key.encode('utf-8')
        return "".join([chr(byte ^ key_bytes[i % key_len]) for i, byte in enumerate(decoded_bytes)])
    except Exception:
        return ""


def build_logo_url(filename: str) -> str:
    if not filename: return ""
    base = filename.rsplit('.', 1)[0]
    return f"{FFHB_LOGO_CDN}/{LOGO_SIZE}/{base}.webp"


def download_image(url: str, dest_path: str):
    try:
        r = requests.get(url, stream=True, timeout=5)
        if r.status_code == 200:
            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception:
        return False


# --- MOTEUR DE BATCH ---

def run_batch_sync(urls):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logger.info(f"📁 Dossier de sortie : {OUTPUT_DIR}")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    print(f"🚀 Démarrage du scan sur {len(urls)} URLs...")
    print("=" * 60)

    for i, url in enumerate(urls, 1):
        # 1. Nettoyage de l'URL (Retour à la racine poule pour stabilité)
        clean_url = sanitize_url(url)

        # Extraction contextuelle AVANT appel
        comp_match = re.search(r'/([^/]+)/poule-(\d+)', clean_url)
        if not comp_match:
            print(f"[{i:02d}] ⚠️  SKIP | Pas d'ID de poule trouvé dans l'URL.")
            continue

        comp_slug, poule_id = comp_match.group(1), comp_match.group(2)

        try:
            # 2. Récupération HTML (pour data-cfk)
            session.headers.update({"Referer": clean_url})
            resp = session.get(clean_url, timeout=10)

            if resp.status_code != 200:
                print(f"[{i:02d}] ❌ FAIL | HTTP {resp.status_code}")
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            data_cfk = soup.find('body').get('data-cfk')

            if not data_cfk:
                print(f"[{i:02d}] ❌ FAIL | Pas de clé CFK.")
                continue

            # 3. Détection intelligente du bloc
            target_block_name = None
            for c in soup.find_all('smartfire-component'):
                name = c.get('name', '')
                if "ranking" in name or "classement" in name or "classification" in name:
                    target_block_name = name
                    break  # On prend le premier trouvé

            if not target_block_name:
                target_block_name = "competitions---new-competition-phase-ranking"

            # 4. Appel API
            saison_match = re.search(r'saison-\d{4}-\d{4}-(\d+)', clean_url)
            saison_id = saison_match.group(1) if saison_match else "21"  # Default to current

            comp_type = "regional"
            if "national" in clean_url:
                comp_type = "national"
            elif "departemental" in clean_url:
                comp_type = "departemental"

            params = {
                "block": target_block_name,
                "ext_saison_id": saison_id,
                "url_competition_type": comp_type,
                "url_competition": comp_slug,
                "ext_poule_id": poule_id
            }

            api_url = f"https://www.ffhandball.fr/wp-json/competitions/v1/computeBlockAttributes?{urlencode(params)}"
            api_resp = session.get(api_url, timeout=10)

            # 5. Traitement Données
            decrypted = ""
            try:
                if api_resp.status_code == 200:
                    decrypted = xor_decipher(api_resp.json(), data_cfk)
            except ValueError:
                pass

            if not decrypted:
                print(f"[{i:02d}] ❌ FAIL | API Error ou Déchiffrement impossible.")
                continue

            data = json.loads(decrypted)
            teams = (data.get('ranking') or data.get('classification') or data.get('classements') or [])

            if not teams:
                print(f"[{i:02d}] ⚠️  VIDE | Liste équipes vide pour poule {poule_id}")
                continue

            # 6. Téléchargement Logos
            new_dl = 0
            existing = 0
            for team in teams:
                club_id = team.get('ext_structureId')
                raw_logo = team.get('structure_logo')

                if club_id and raw_logo:
                    local_path = os.path.join(OUTPUT_DIR, f"{club_id}.webp")
                    if not os.path.exists(local_path):
                        if download_image(build_logo_url(raw_logo), local_path):
                            new_dl += 1
                    else:
                        existing += 1

            print(f"[{i:02d}] ✅ OK   | Poule {poule_id} : {new_dl} téléchargés, {existing} déjà présents.")

        except Exception as e:
            print(f"[{i:02d}] 🔥 ERR  | {e}")

    print("=" * 60)
    print("Terminé.")


if __name__ == "__main__":
    run_batch_sync(TARGET_URLS)