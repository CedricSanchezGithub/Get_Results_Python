import base64
import json
import logging
import re
from urllib.parse import urlencode
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup

# Import de la logique partagée
from src.scraping.get_ranking import parse_ranking_list

logger = logging.getLogger(__name__)


def xor_decipher(encoded_str: str, key: str) -> str:
    """Déchiffre la réponse API."""
    try:
        decoded_bytes = base64.b64decode(encoded_str)
        result = []
        key_len = len(key)
        key_bytes = key.encode('utf-8')
        for i, byte in enumerate(decoded_bytes):
            result.append(chr(byte ^ key_bytes[i % key_len]))
        return "".join(result)
    except Exception as e:
        logger.error(f"Erreur déchiffrement XOR : {e}")
        return ""


def _extract_context_from_url(url: str) -> Dict[str, str]:
    params = {}
    patterns = {
        'ext_saison_id': r'saison-\d{4}-\d{4}-(\d+)',
        'url_competition_type': r'saison-[^/]+/([^/]+)/',
        'numero_journee': r'journee-(\d+)'
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, url)
        if match: params[key] = match.group(1)

    comp_match = re.search(r'/([^/]+)/poule-(\d+)', url)
    if comp_match:
        params['url_competition'] = comp_match.group(1)
        params['ext_poule_id'] = comp_match.group(2)

    return params


def _find_ranking_block_name(soup: BeautifulSoup) -> str:
    for comp in soup.find_all('smartfire-component'):
        name = comp.get('name', '')
        if any(k in name for k in ["ranking", "classement", "classification"]):
            return name
    return "competitions---new-competition-phase-ranking"


def get_ranking_from_api(url_page: str, poule_id_fallback: str = None) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """
    Orchestre la récupération du classement et des métadonnées via l'API sécurisée.

    Cette fonction :
    1. Récupère la clé de déchiffrement (data-cfk) sur la page HTML.
    2. Construit l'appel API 'computeBlockAttributes' avec le contexte de la poule.
    3. Déchiffre la réponse XOR/Base64.
    4. Extrait le nom officiel de la phase et la liste structurée des équipes.

    Args:
        url_page (str): L'URL publique de la page (ex: .../poule-123/classements/).
        poule_id_fallback (str, optional): ID de secours si l'URL est malformée.

    Returns:
        Tuple[Optional[str], List[Dict]]:
            - Le nom officiel de la phase (ex: "+16 Ans M Preregionale...").
            - La liste standardisée des rangs et stats par équipe.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": url_page
    })

    try:
        # 1. Page Initiale (Récupération de la clé contextuelle)
        logger.info(f"🌍 Fetch page initiale: {url_page}")
        resp = session.get(url_page, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        body_tag = soup.find('body')
        data_cfk = body_tag.get('data-cfk') if body_tag else None

        if not data_cfk:
            logger.error(f"❌ Clé 'data-cfk' introuvable sur {url_page}. Impossible de déchiffrer l'API.")
            return None, []

        # 2. Construction de l'appel API
        context = _extract_context_from_url(url_page)
        if poule_id_fallback and 'ext_poule_id' not in context:
            context['ext_poule_id'] = poule_id_fallback

        block_name = _find_ranking_block_name(soup)

        api_params = {
            "block": block_name,
            "ext_saison_id": context.get('ext_saison_id', ''),
            "url_competition_type": context.get('url_competition_type', 'regional'),
            "url_competition": context.get('url_competition', ''),
            "ext_poule_id": context.get('ext_poule_id', ''),
        }

        # Ajout optionnel de la journée si présente (parfois requis pour les classements partiels)
        if 'numero_journee' in context:
            api_params['numero_journee'] = context['numero_journee']

        api_url = f"https://www.ffhandball.fr/wp-json/competitions/v1/computeBlockAttributes?{urlencode(api_params)}"

        logger.debug(f"📡 Appel API: {api_url}")
        api_resp = session.get(api_url, timeout=10)

        if api_resp.status_code >= 400:
            logger.error(f"❌ Erreur API HTTP {api_resp.status_code}")
            return None, []

        # 3. Déchiffrement & Parsing JSON
        decrypted_json_str = xor_decipher(api_resp.json(), data_cfk)

        if not decrypted_json_str:
            logger.warning("⚠️ Échec du déchiffrement ou réponse vide.")
            return None, []

        data = json.loads(decrypted_json_str)

        # 4. Extraction des Données
        # A. Le Titre Officiel (Exploration des clés probables)
        official_title = (
                data.get('title') or
                data.get('label') or
                data.get('nom') or
                data.get('competition', {}).get('name')
        )

        # Nettoyage HTML éventuel dans le titre (ex: &amp;)
        if official_title and isinstance(official_title, str):
            official_title = BeautifulSoup(official_title, "html.parser").get_text(strip=True)

        # B. La Liste du Classement
        raw_ranking_list = (
                data.get('ranking') or
                data.get('classification') or
                data.get('rows') or
                data.get('classements') or
                []
        )

        ranking_cleaned = parse_ranking_list(raw_ranking_list)

        logger.info(f"✅ Données récupérées : Titre='{official_title}' | {len(ranking_cleaned)} équipes")

        return official_title, ranking_cleaned

    except Exception as e:
        logger.exception(f"🔥 Exception critique dans get_ranking_from_api : {e}")
        return None, []