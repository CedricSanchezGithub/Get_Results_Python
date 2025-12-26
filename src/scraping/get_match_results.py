import hashlib
import logging
import json
import html
import os
import re
import time

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional

from src.config import DEBUG_DIR
from src.scraping.get_ranking import extract_ranking_from_soup
from src.utils.format_date import format_date

logger = logging.getLogger(__name__)


def _save_debug_html(url: str, content: str, prefix: str = ""):
    """
    Sauvegarde le HTML brut dans le dossier debug pour analyse.
    Génère un nom de fichier unique basé sur l'URL et le timestamp.
    """
    try:
        # Création d'un hash court de l'URL pour éviter les caractères interdits dans les noms de fichiers
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # Nettoyage du préfixe
        safe_prefix = "".join([c for c in prefix if c.isalnum() or c in ('-', '_')]).strip()
        filename = f"{timestamp}_{safe_prefix}_{url_hash}.html"

        filepath = os.path.join(DEBUG_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"💾 HTML brut sauvegardé : {filename}")

    except Exception as e:
        logger.warning(f"⚠️ Impossible de sauvegarder le HTML de debug : {e}")


def fetch_html(url: str, save_debug: bool = False, debug_prefix: str = "dump") -> Optional[str]:
    """
    Récupère le HTML brut via requests.
    Args:
        url: L'URL cible.
        save_debug: Si True, sauvegarde le fichier localement.
        debug_prefix: Préfixe pour le nom du fichier de debug.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        html_text = response.text

        # HOOK DE DEBUG
        if save_debug:
            _save_debug_html(url, html_text, debug_prefix)

        return html_text

    except Exception as e:
        logger.error(f"Erreur réseau sur {url} : {e}")
        return None


def get_matches_from_url(url: str, category: str) -> Tuple[
    List[Dict], List[Dict], List[Dict]]:
    """
    Fonction principale (Orchestrateur) :
    1. Récupère le HTML
    2. Extrait les matchs
    3. Extrait la pagination
    4. Extrait le classement (NOUVEAU)
    """
    html_content = fetch_html(url)
    if not html_content:
        return [], [], []

    soup = BeautifulSoup(html_content, "html.parser")

    current_journee = _extract_journee_from_url(url)
    matches = _extract_matches_from_soup(soup, category, current_journee)
    journees_meta = _extract_pagination_meta(soup, category)

    ranking = extract_ranking_from_soup(soup)
    if ranking:
        logger.info(f"📊 Classement récupéré : {len(ranking)} équipes.")

    return matches, journees_meta, ranking


def _extract_journee_from_url(url: str) -> Optional[str]:
    """Extrait le numéro de journée (ex: '1') depuis l'URL."""
    match = re.search(r"journee-(\d+)", url)
    return match.group(1) if match else None


def _extract_matches_from_soup(soup: BeautifulSoup, category: str, default_journee: Optional[str]) -> List[Dict]:
    """Cherche le composant 'rencontre-list' et parse chaque match."""
    component = soup.find("smartfire-component", attrs={"name": "competitions---rencontre-list"})

    if not component:
        return []

    results = []
    try:
        raw_attr = component.get("attributes", "{}")
        json_data = json.loads(html.unescape(raw_attr))
        rencontres = json_data.get("rencontres", [])

        logger.info(f"📊 Traitement de {len(rencontres)} matchs pour {category} (J{default_journee})")

        for match_json in rencontres:
            processed_match = _process_single_match(match_json, category, default_journee)
            if processed_match:
                results.append(processed_match)

    except Exception as e:
        logger.error(f"Erreur parsing JSON rencontres pour {category}: {e}")

    return results


def _process_single_match(match: Dict, category: str, default_journee: Optional[str]) -> Optional[Dict]:
    """
    Traite un match individuel : Parsing date, Validation, Construction dict.
    Retourne None si le match est invalide.
    """
    raw_date = match.get("date")
    formatted_date = None

    # --- BLOC LOGIQUE DATE (Ta version debuggée) ---
    if raw_date:
        # Log de debug profond (Inspection)
        logger.info(f"🔍 PRE-PARSE INPUT: '{raw_date}' | Repr: {repr(raw_date)} | Type: {type(raw_date)}")

        dt_obj = format_date(raw_date)
        if dt_obj:
            formatted_date = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"   ✅ Date OK: {formatted_date}")
        else:
            logger.warning(f"   ❌ Date KO (Parse fail)")

    if not formatted_date:
        # On loggue le contenu complet si la date manque, pour comprendre pourquoi
        match_debug = json.dumps(match, ensure_ascii=False)
        logger.warning(
            f"⚠️ Date invalide/absente. Match ignoré: "
            f"{match.get('equipe1Libelle')} vs {match.get('equipe2Libelle')} | JSON: {match_debug}"
        )
        return None

    # Construction de l'objet final
    return {
        "match_date": formatted_date,
        "team_1_name": match.get("equipe1Libelle", "Nom non disponible"),
        "team_1_score": match.get("equipe1Score") if match.get("equipe1Score") != "" else None,
        "team_2_name": match.get("equipe2Libelle", "Nom non disponible"),
        "team_2_score": match.get("equipe2Score") if match.get("equipe2Score") != "" else None,
        "match_link": None,
        "competition": category,
        "journee": match.get("journeeNumero", default_journee)
    }


def _extract_pagination_meta(soup: BeautifulSoup, category: str) -> List[Dict]:
    """Gère la logique complexe de récupération de la liste des journées."""
    # Il y a deux noms de composants possibles selon les pages
    selector = soup.find("smartfire-component", attrs={"name": "competitions---poule-selector"})
    if not selector:
        selector = soup.find("smartfire-component", attrs={"name": "competitions---journee-selector"})

    if not selector:
        return []

    try:
        raw_attr = selector.get("attributes", "{}")
        main_json = json.loads(html.unescape(raw_attr))

        # Stratégie en entonnoir pour trouver 'journees'
        raw_journees = (
                main_json.get("journees") or
                (main_json.get("poule") or {}).get("journees") or
                (main_json.get("selected_poule") or {}).get("journees")
        )

        if isinstance(raw_journees, str):
            return json.loads(raw_journees)
        elif isinstance(raw_journees, list):
            return raw_journees

    except Exception as e:
        logger.warning(f"Impossible d'extraire la liste des journées pour {category}: {e}")

    return []