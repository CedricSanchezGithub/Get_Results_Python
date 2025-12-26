import logging
import re
from typing import List, Dict, Any, Tuple

from src.saving.db_writer import db_writer_results
from src.scraping.get_match_results import get_matches_from_url

# Configuration du logger au niveau du module
logger = logging.getLogger(__name__)


def get_all(url_start: str, category: str):
    """
    Orchestrateur principal : Scrape toutes les journées d'une poule donnée et sauvegarde.
    """
    logger.info(f"🚀 [Orchestrator] Démarrage scraping '{category}'")

    all_match_data = []

    # 1. Étape Initiale
    initial_matches, journees_meta = _fetch_initial_page(url_start, category)
    all_match_data.extend(initial_matches)

    # 2. Calcul des URLs à visiter
    urls_to_visit = _build_pagination_urls(url_start, journees_meta)

    # 3. Scraping des autres journées
    paginated_matches = _fetch_paginated_pages(urls_to_visit, category)
    all_match_data.extend(paginated_matches)

    # 4. Sauvegarde
    logger.info(f"🏁 Fin du scraping pour '{category}'. Total: {len(all_match_data)} matchs. Écriture BDD...")
    db_writer_results(all_match_data, category)


def _fetch_initial_page(url: str, category: str) -> Tuple[List[Dict], List[Dict]]:
    """Récupère la première page et ses métadonnées de navigation."""
    logger.info(f"Traitement URL initiale : {url}")
    matches, meta = get_matches_from_url(url, category)

    if matches:
        logger.info(f"  -> {len(matches)} matchs trouvés sur la page initiale.")

    return matches, meta


def _build_pagination_urls(url_start: str, journees_meta: List[Dict]) -> List[str]:
    """
    Génère la liste propre des URLs cibles pour les autres journées.
    Contient toute la logique de Regex et de nettoyage des clés.
    """
    if not journees_meta:
        logger.warning("⚠️ Aucune métadonnée de journée trouvée. Pagination impossible.")
        return []

    logger.info(f"  -> {len(journees_meta)} journées détectées dans la structure.")

    # Debug structurel pour identifier les clés (comme vu précédemment)
    if len(journees_meta) > 0:
        logger.debug(f"  🔍 [DEBUG STRUCT] Keys premier élément: {list(journees_meta[0].keys())}")

    # Construction du pattern d'URL
    # Ex: transforme ".../journee-1/" en ".../journee-{}/"
    base_url_pattern = re.sub(r"journee-\d+/?", "journee-{}/", url_start)

    # Fallback si l'URL n'a pas le format attendu
    if base_url_pattern == url_start:
        if not base_url_pattern.endswith("/"):
            base_url_pattern += "/"
        base_url_pattern += "journee-{}/"

    target_urls = []

    for journee in journees_meta:
        # Logique robuste de récupération du numéro (Fix J7/J10)
        num = journee.get("journeeNumero") or journee.get("journee_numero") or journee.get("numero")

        if not num:
            logger.warning(f"  ⚠️ Numéro introuvable dans métadonnée : {journee}. Ignoré.")
            continue

        # On ne génère pas l'URL si c'est celle qu'on vient de scraper (url_start)
        # On compare les strings pour être sûr (ex: "journee-1" dans l'url)
        if f"journee-{num}" in url_start:
            continue

        final_url = base_url_pattern.format(num)
        target_urls.append(final_url)

    return target_urls


def _fetch_paginated_pages(urls: List[str], category: str) -> List[Dict]:
    """Boucle sur les URLs générées et récupère les matchs."""
    results = []
    for url in urls:
        # logger.debug(f"    -> Scraping paginé : {url}")
        page_matches, _ = get_matches_from_url(url, category)
        if page_matches:
            results.extend(page_matches)

    if results:
        logger.info(f"  -> {len(results)} matchs supplémentaires récupérés via pagination.")

    return results