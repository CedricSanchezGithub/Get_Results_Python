import logging
import re
from typing import List, Dict, Tuple, Optional

from src.saving.db_writer import db_writer_results, db_writer_ranking
from src.scraping.get_match_results import get_matches_from_url
from src.scraping.get_ranking_api import get_ranking_from_api

logger = logging.getLogger(__name__)


def _extract_poule_id(url: str) -> Optional[str]:
    """Extrait l'ID de la poule depuis l'URL."""
    match = re.search(r'poule-(\d+)', url)
    return match.group(1) if match else None


def get_all(url_start: str, category: str):
    """
    Orchestre le scraping des matchs et du classement (HTML + API).
    """
    logger.info(f"🚀 [Start] Scraping '{category}' via {url_start}")

    all_match_data = []
    latest_ranking = []

    # 1. Scraping Page Initiale
    initial_matches, journees_meta, initial_ranking = _fetch_initial_page(url_start, category)
    all_match_data.extend(initial_matches)

    if initial_ranking:
        latest_ranking = initial_ranking

    # 2. Scraping Pagination (Matchs + Fallback Classement HTML)
    urls_to_visit = _build_pagination_urls(url_start, journees_meta)
    paginated_matches, paginated_ranking = _fetch_paginated_pages(urls_to_visit, category)
    all_match_data.extend(paginated_matches)

    # Si pas de classement trouvé en page 1, on prend celui de la pagination
    if not latest_ranking and paginated_ranking:
        latest_ranking = paginated_ranking

    # 3. Tentative API (Prioritaire pour le classement)
    poule_id = _extract_poule_id(url_start)
    api_ranking = get_ranking_from_api(url_start, poule_id_fallback=poule_id)

    if api_ranking:
        latest_ranking = api_ranking  # L'API écrase le HTML car plus fiable
        logger.info(f"✅ Classement récupéré via API ({len(api_ranking)} équipes).")
    elif latest_ranking:
        logger.info(f"ℹ️ Utilisation du classement HTML ({len(latest_ranking)} équipes).")

    # 4. Sauvegardes
    if all_match_data:
        db_writer_results(all_match_data, category)
        logger.info(f"💾 Matchs sauvegardés : {len(all_match_data)}")
    else:
        logger.warning(f"⚠️ Aucun match trouvé pour '{category}'")

    if latest_ranking:
        db_writer_ranking(latest_ranking, category)
        logger.info("💾 Classement sauvegardé.")
    else:
        logger.warning(f"⚠️ Aucun classement trouvé (ni API, ni HTML) pour '{category}'")

    logger.info(f"🏁 [End] Scraping terminé pour '{category}'")


def _fetch_initial_page(url: str, category: str) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Récupère matchs, métadonnées et classement de la première page."""
    matches, meta, ranking = get_matches_from_url(url, category)
    return matches, meta, ranking


def _build_pagination_urls(url_start: str, journees_meta: List[Dict]) -> List[str]:
    """Construit les URLs de pagination."""
    if not journees_meta:
        return []

    # Construction du pattern (journee-X -> journee-{}/)
    base_url_pattern = re.sub(r"journee-\d+/?", "journee-{}/", url_start)
    if base_url_pattern == url_start:
        if not base_url_pattern.endswith("/"):
            base_url_pattern += "/"
        base_url_pattern += "journee-{}/"

    target_urls = []
    for journee in journees_meta:
        num = journee.get("journeeNumero") or journee.get("journee_numero") or journee.get("numero")

        # On ignore si pas de numéro ou si c'est l'URL de départ
        if not num or f"journee-{num}" in url_start:
            continue

        target_urls.append(base_url_pattern.format(num))

    return target_urls


def _fetch_paginated_pages(urls: List[str], category: str) -> Tuple[List[Dict], List[Dict]]:
    """Scrape les pages suivantes."""
    results = []
    found_ranking = []

    for url in urls:
        page_matches, _, page_ranking = get_matches_from_url(url, category)

        if page_matches:
            results.extend(page_matches)

        # On récupère le classement au passage si on ne l'avait pas encore
        if page_ranking and not found_ranking:
            found_ranking = page_ranking

    return results, found_ranking