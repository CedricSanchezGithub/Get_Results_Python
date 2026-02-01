#!/usr/bin/env python3
"""
Script de test du scraping en mode "dry-run".
Aucune dépendance externe requise (pas de MySQL, pas d'API backend).

Usage:
    python scripts/dry_run_scrape.py [URL]

Exemple:
    python scripts/dry_run_scrape.py "https://www.ffhandball.fr/competitions/.../poule-XXXXX/journee-1/"
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Import des modules de scraping (sans dépendances DB/API)
from src.scraping.get_match_results import get_matches_from_url
from src.scraping.get_ranking_api import get_ranking_from_api

# URL par défaut pour les tests
DEFAULT_URL = "https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-13-feminins-28964/poule-175593/journee-1/"


def print_separator(title: str = ""):
    """Affiche un séparateur visuel."""
    if title:
        logger.info(f"\n{'='*60}")
        logger.info(f" {title}")
        logger.info(f"{'='*60}")
    else:
        logger.info("-" * 60)


def format_score(score) -> str:
    """Formate un score (gère None)."""
    return str(score) if score is not None else "-"


def dry_run_scrape(url: str):
    """
    Exécute le scraping complet d'une URL sans envoyer les données.

    Args:
        url: URL de la page FFHandball à scraper
    """
    print_separator("DRY-RUN SCRAPING TEST")
    logger.info(f"URL: {url}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ==========================================================================
    # 1. SCRAPING DES MATCHS (HTML)
    # ==========================================================================
    print_separator("1. SCRAPING DES MATCHS")

    try:
        matches, journees_meta, _ = get_matches_from_url(url, "TEST")

        if matches:
            logger.info(f"✅ {len(matches)} match(s) trouvé(s)\n")

            for i, match in enumerate(matches, 1):
                date_str = match.get('match_date', 'Date inconnue')
                team1 = match.get('team_1_name', '?')
                team2 = match.get('team_2_name', '?')
                score1 = format_score(match.get('team_1_score'))
                score2 = format_score(match.get('team_2_score'))
                journee = match.get('journee', '?')

                logger.info(f"  Match {i}:")
                logger.info(f"    📅 {date_str}")
                logger.info(f"    🏠 {team1}: {score1}")
                logger.info(f"    🚌 {team2}: {score2}")
                logger.info(f"    📍 Journée {journee}")
                logger.info("")
        else:
            logger.warning("⚠️ Aucun match trouvé")

        if journees_meta:
            logger.info(f"📋 Métadonnées pagination: {len(journees_meta)} journée(s) disponible(s)")

    except Exception as e:
        logger.error(f"❌ Erreur scraping matchs: {e}")
        matches = []

    # ==========================================================================
    # 2. SCRAPING DU CLASSEMENT (API + XOR)
    # ==========================================================================
    print_separator("2. SCRAPING DU CLASSEMENT (API)")

    # Construire l'URL du classement
    base_url = url.split("journee-")[0] if "journee-" in url else url
    if not base_url.endswith("/"):
        base_url += "/"
    ranking_url = f"{base_url}classements/"

    logger.info(f"URL classement: {ranking_url}\n")

    try:
        official_phase_name, ranking = get_ranking_from_api(ranking_url)

        if official_phase_name:
            logger.info(f"✨ Phase officielle: \"{official_phase_name}\"\n")
        else:
            logger.warning("⚠️ Nom de phase non trouvé\n")

        if ranking:
            logger.info(f"✅ {len(ranking)} équipe(s) dans le classement\n")

            # Afficher le classement sous forme de tableau
            logger.info(f"  {'Rg':<4} {'Équipe':<35} {'Pts':<5} {'J':<4} {'G':<4} {'N':<4} {'P':<4} {'Diff':<6}")
            logger.info(f"  {'-'*4} {'-'*35} {'-'*5} {'-'*4} {'-'*4} {'-'*4} {'-'*4} {'-'*6}")

            for team in ranking:
                rank = team.get('rank', '-')
                name = team.get('team_name', '?')[:35]
                pts = team.get('points', '-')
                played = team.get('matches_played', '-')
                won = team.get('won', '-')
                draws = team.get('draws', '-')
                lost = team.get('lost', '-')
                diff = team.get('goal_diff', '-')

                # Formater le diff avec signe
                if isinstance(diff, int):
                    diff_str = f"+{diff}" if diff > 0 else str(diff)
                else:
                    diff_str = str(diff)

                logger.info(f"  {str(rank):<4} {name:<35} {str(pts):<5} {str(played):<4} {str(won):<4} {str(draws):<4} {str(lost):<4} {diff_str:<6}")
        else:
            logger.warning("⚠️ Aucun classement trouvé")

    except Exception as e:
        logger.error(f"❌ Erreur scraping classement: {e}")
        ranking = []
        official_phase_name = None

    # ==========================================================================
    # 3. RÉSUMÉ
    # ==========================================================================
    print_separator("RÉSUMÉ")

    logger.info(f"  Matchs extraits:     {len(matches)}")
    logger.info(f"  Équipes classées:    {len(ranking) if ranking else 0}")
    logger.info(f"  Phase officielle:    {official_phase_name or 'Non trouvée'}")

    print_separator()

    # ==========================================================================
    # 4. DONNÉES BRUTES (JSON)
    # ==========================================================================
    if "--json" in sys.argv:
        print_separator("DONNÉES BRUTES (JSON)")

        output = {
            "url": url,
            "official_phase_name": official_phase_name,
            "matches_count": len(matches),
            "matches": matches[:3] if matches else [],  # Limiter à 3 pour lisibilité
            "ranking_count": len(ranking) if ranking else 0,
            "ranking": ranking[:5] if ranking else []   # Limiter à 5
        }

        logger.info(json.dumps(output, indent=2, default=str, ensure_ascii=False))

    return len(matches) > 0 or (ranking and len(ranking) > 0)


def main():
    """Point d'entrée principal."""
    # Récupérer l'URL depuis les arguments ou utiliser la valeur par défaut
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        url = sys.argv[1]
    else:
        url = DEFAULT_URL
        logger.info(f"Utilisation de l'URL par défaut")

    success = dry_run_scrape(url)

    if success:
        logger.info("\n✅ Test réussi - Le scraping fonctionne correctement")
        sys.exit(0)
    else:
        logger.error("\n❌ Test échoué - Aucune donnée extraite")
        sys.exit(1)


if __name__ == "__main__":
    main()
