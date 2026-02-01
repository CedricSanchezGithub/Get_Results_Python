import logging
import re
from typing import List, Dict, Tuple, Optional

from src.models.models import MatchIngest
from src.saving.api_client import IngestClient
from src.scraping.get_match_results import get_matches_from_url


logger = logging.getLogger(__name__)

# Instanciation unique du client (ou injection de dépendance)
ingest_client = IngestClient()


def _extract_poule_id(url: str) -> Optional[str]:
    match = re.search(r'poule-(\d+)', url)
    return match.group(1) if match else None


def _map_to_ingest_model(raw_match: Dict, category: str, pool_id: str) -> Optional[MatchIngest]:
    """Transforme le dictionnaire brut du scraper en Modèle Pydantic Strict."""
    try:
        # Mapping explicite des champs
        # Note: 'journee' du scraper devient 'round' pour l'API
        return MatchIngest(
            match_date=raw_match['match_date'],  # Doit déjà être un datetime ou str ISO valide
            team_1_name=raw_match['team_1_name'],
            team_1_score=raw_match['team_1_score'],
            team_2_name=raw_match['team_2_name'],
            team_2_score=raw_match['team_2_score'],
            category=category,
            pool_id=pool_id,
            official_phase_name=raw_match.get('official_phase_name'),
            round=str(raw_match.get('journee')) if raw_match.get('journee') else None
        )
    except Exception as e:
        logger.warning(f"⚠️ Donnée invalide ignorée : {e} | Data: {raw_match}")
        return None


def get_all(url_start: str, category: str):
    logger.info(f"🚀 [Start] Scraping '{category}' via {url_start}")

    all_match_data = []

    # ... (Logique existante de scraping inchangée : fetch_initial_page, pagination ...) ...
    # Supposons que tu aies récupéré 'all_match_data' (liste de dicts) comme avant.

    # 1. Scraping Page Initiale
    initial_matches, journees_meta, _ = _fetch_initial_page(url_start, category)
    all_match_data.extend(initial_matches)

    # 2. Scraping Pagination
    urls_to_visit = _build_pagination_urls(url_start, journees_meta)
    paginated_matches, _ = _fetch_paginated_pages(urls_to_visit, category)
    all_match_data.extend(paginated_matches)

    # 3. Récupération API (Classement) -> Pour l'instant on ignore le classement dans ce refacto
    # car ton ticket ne mentionne que l'endpoint /api/ingest/matches.
    # Si un endpoint /api/ingest/rankings existe, il faudra reproduire la logique.

    # 4. Transformation et Envoi via API
    poule_id = _extract_poule_id(url_start)
    effective_pool_id = poule_id if poule_id else f"UNKNOWN_{category}"

    if all_match_data:
        # Transformation Dict -> Pydantic
        ingest_batch = []
        for m in all_match_data:
            model = _map_to_ingest_model(m, category, effective_pool_id)
            if model:
                ingest_batch.append(model)

        # Envoi HTTP
        if ingest_batch:
            success = ingest_client.send_matches(ingest_batch)
            if success:
                logger.info(f"💾 {len(ingest_batch)} Matchs envoyés au Backend.")
            else:
                logger.error("❌ Echec de l'envoi au Backend.")
    else:
        logger.warning(f"⚠️ Aucun match trouvé pour '{category}'")

    logger.info(f"🏁 [End] Scraping terminé pour '{category}'")


def _fetch_initial_page(url: str, category: str) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Récupère matchs, métadonnées et classement de la première page."""
    matches, meta, ranking = get_matches_from_url(url, category)
    return matches, meta, ranking


def _build_pagination_urls(url_start: str, journees_meta: List[Dict]) -> List[str]:
    """Construit les URLs de pagination."""
    if not journees_meta:
        return []

    base_url_pattern = re.sub(r"journee-\d+/?", "journee-{}/", url_start)
    if base_url_pattern == url_start:
        if not base_url_pattern.endswith("/"):
            base_url_pattern += "/"
        base_url_pattern += "journee-{}/"

    target_urls = []
    for journee in journees_meta:
        num = journee.get("journeeNumero") or journee.get("journee_numero") or journee.get("numero")

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

        if page_ranking and not found_ranking:
            found_ranking = page_ranking

    return results, found_ranking