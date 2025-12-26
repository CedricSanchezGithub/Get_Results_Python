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


def get_ranking_from_api(url_page: str, poule_id_fallback: str = None) -> List[Dict[str, Any]]:
    """Récupère et déchiffre le classement via API."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": url_page
    })

    try:
        # 1. Page Initiale (Clé + Block)
        resp = session.get(url_page, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        data_cfk = soup.find('body').get('data-cfk') if soup.find('body') else None
        if not data_cfk:
            logger.error(f"❌ Clé 'data-cfk' introuvable sur {url_page}")
            return []

        # 2. Appel API
        context = _extract_context_from_url(url_page)
        if poule_id_fallback and 'ext_poule_id' not in context:
            context['ext_poule_id'] = poule_id_fallback

        api_params = {
            "block": _find_ranking_block_name(soup),
            "ext_saison_id": context.get('ext_saison_id', ''),
            "url_competition_type": context.get('url_competition_type', 'regional'),
            "url_competition": context.get('url_competition', ''),
            "ext_poule_id": context.get('ext_poule_id', ''),
        }
        if 'numero_journee' in context:
            api_params['numero_journee'] = context['numero_journee']

        api_url = f"https://www.ffhandball.fr/wp-json/competitions/v1/computeBlockAttributes?{urlencode(api_params)}"

        api_resp = session.get(api_url, timeout=10)
        if api_resp.status_code >= 400: return []

        # 3. Déchiffrement & Parsing
        decrypted = xor_decipher(api_resp.json(), data_cfk)
        if not decrypted: return []

        data = json.loads(decrypted)

        # On cherche la liste brute
        ranking_list = (
                data.get('ranking') or
                data.get('classification') or
                data.get('rows') or
                data.get('classements') or
                []
        )

        # 4. Utilisation du parser centralisé !
        return parse_ranking_list(ranking_list)

    except Exception as e:
        logger.error(f"Erreur API Ranking : {e}")
        return []