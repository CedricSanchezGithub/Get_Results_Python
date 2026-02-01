import json
import logging
import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

sys.path.append(os.path.join(os.path.dirname(__file__)))

from src.utils.logging_config import configure_logging
from src.scraping.get_ranking_api import xor_decipher, _extract_context_from_url, _find_ranking_block_name

configure_logging()
logger = logging.getLogger("DEBUG_DUMP")


def dump_api_response(url_page: str, output_filename: str = "debug_api_dump.json"):
    """
    Récupère, déchiffre et sauvegarde la réponse brute de l'API FFHandball.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": url_page
    })

    logger.info(f"1. 🌍 Analyse de la page HTML : {url_page}")
    try:
        resp = session.get(url_page, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"❌ Impossible d'accéder à la page : {e}")
        return

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Récupération de la clé de déchiffrement
    body_tag = soup.find('body')
    data_cfk = body_tag.get('data-cfk') if body_tag else None

    if not data_cfk:
        logger.error(
            "❌ CLÉ MANQUANTE : Impossible de trouver 'data-cfk' dans le <body>. FFHandball a peut-être changé sa sécurité.")
        return

    logger.info(f"🔑 Clé trouvée (data-cfk) : {data_cfk[:10]}...")

    # Construction de la requête API (Réutilisation de ta logique)
    context = _extract_context_from_url(url_page)
    block_name = _find_ranking_block_name(soup)

    logger.info(f"🧩 Contexte extrait : {context}")
    logger.info(f"🧩 Block name : {block_name}")

    api_params = {
        "block": block_name,
        "ext_saison_id": context.get('ext_saison_id', ''),
        "url_competition_type": context.get('url_competition_type', 'regional'),
        "url_competition": context.get('url_competition', ''),
        "ext_poule_id": context.get('ext_poule_id', ''),
    }

    # Gestion spécifique pour les journées si présentes dans l'URL
    if 'numero_journee' in context:
        api_params['numero_journee'] = context['numero_journee']

    api_url = f"https://www.ffhandball.fr/wp-json/competitions/v1/computeBlockAttributes?{urlencode(api_params)}"

    logger.info(f"2. 📡 Appel de l'API cachée : {api_url}")

    try:
        api_resp = session.get(api_url, timeout=10)
        api_resp.raise_for_status()

        # Le payload chiffré
        encrypted_data = api_resp.json()

        # Déchiffrement
        logger.info("3. 🔓 Déchiffrement du payload...")
        decrypted_json_str = xor_decipher(encrypted_data, data_cfk)

        if not decrypted_json_str:
            logger.error("❌ Échec du déchiffrement (résultat vide).")
            return

        data = json.loads(decrypted_json_str)

        # Sauvegarde
        output_path = os.path.join("data", "debug_html",
                                   output_filename)  # Je garde ton dossier data/debug_html par habitude
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        logger.info(f"✅ SUCCÈS ! Dump JSON complet sauvegardé ici : {output_path}")
        logger.info("👉 Ouvre ce fichier pour trouver les champs 'logo', 'team', etc.")

    except Exception as e:
        logger.exception(f"🔥 Erreur critique durant le process API : {e}")


if __name__ == "__main__":
    # URL Cible : Une poule active
    target_url = "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/18-ans-f-2e-division-28369/poule-179943/"
    dump_api_response(target_url, "dump_poule_complete.json")