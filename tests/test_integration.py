from unittest.mock import patch

from run_daily_scraping import run_daily_scraping


REAL_TEST_URLS = [
    {
        "id": "1",
        "category": "SF",
        "url": "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/16-ans-f-prenationale-28365/poule-169120/journee-1/",
    },
    {
        "id": "2",
        "category": "-18F",
        "url": "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/18-ans-f-2e-division-28369/poule-179943/journee-1/",
    },
]


class TestRunDailyScrapingIntegration:
    """Tests d'intégration - scraping réel vers ffhandball.fr."""

    @patch("run_daily_scraping.update_log_entry")
    @patch("run_daily_scraping.create_log_entry", return_value=1)
    @patch("src.scraping.get_all.ingest_client.send_teams")
    @patch("src.scraping.get_all.ingest_client.send_matches")
    @patch("src.scraping.get_all.ingest_client.send_rankings")
    @patch("run_daily_scraping.get_urls_from_api")
    def test_scraping_real_urls(
        self,
        mock_urls,
        mock_send_rankings,
        mock_send_matches,
        mock_send_teams,
        mock_create,
        mock_update,
    ):
        """Test avec vraies URLs - scrape réellement ffhandball.fr."""
        mock_urls.return_value = REAL_TEST_URLS
        mock_send_teams.return_value = {}  # mapping vide → team_ids seront null
        mock_send_matches.return_value = True
        mock_send_rankings.return_value = True

        run_daily_scraping(max_workers=1, skip_config_check = True)

        print(f"\n=== DONNÉES ÉQUIPES CAPTURÉES ===")
        if mock_send_teams.call_count > 0:
            for call in mock_send_teams.call_args_list:
                for team in call[0][0]:
                    print(f"  {team.team_name} | logo: {team.logo_filename or 'N/A'}")
        else:
            print("  (Aucune équipe trouvée)")

        print(f"\n=== DONNÉES MATCHS CAPTURÉES ===")
        if mock_send_matches.call_count > 0:
            for call in mock_send_matches.call_args_list:
                for match in call[0][0]:
                    print(
                        f"  team_1_id={match.team_1_id} {match.team_1_score or '?'} - {match.team_2_score or '?'} team_2_id={match.team_2_id}"
                    )
                    print(
                        f"    Category: {match.category}, Pool: {match.pool_id}, Date: {match.match_date}"
                    )
        else:
            print("  (Aucun match trouvé)")

        print(f"\n=== DONNÉES RANKINGS CAPTURÉES ===")
        if mock_send_rankings.call_count > 0:
            for call in mock_send_rankings.call_args_list:
                for rank in call[0][0]:
                    print(
                        f"  #{rank.rank} team_id={rank.team_id} - {rank.points} pts [{rank.category}]"
                    )
        else:
            print("  (Aucun classement trouvé)")

        assert mock_send_teams.called or mock_send_matches.called or mock_send_rankings.called
