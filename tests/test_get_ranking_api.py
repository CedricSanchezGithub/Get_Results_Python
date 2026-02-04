import pytest
import base64
from unittest.mock import patch, MagicMock

from src.scraping.get_ranking_api import (
    xor_decipher,
    get_ranking_from_api,
    _extract_context_from_url,
    _find_ranking_block_name,
)


class TestXorDecipher:
    """Tests du déchiffrement XOR."""

    def test_xor_decipher_basic(self):
        """Vérifie le déchiffrement d'une chaîne simple."""
        key = "testkey"
        plaintext = '{"ranking": []}'
        # Chiffrement manuel pour le test
        encrypted_bytes = bytes([
            ord(c) ^ ord(key[i % len(key)])
            for i, c in enumerate(plaintext)
        ])
        encoded = base64.b64encode(encrypted_bytes).decode('utf-8')

        result = xor_decipher(encoded, key)
        assert result == plaintext

    def test_xor_decipher_with_unicode(self):
        """Vérifie le déchiffrement avec caractères spéciaux."""
        key = "abc"
        plaintext = '{"title": "Équipe"}'
        encrypted_bytes = bytes([
            ord(c) ^ ord(key[i % len(key)])
            for i, c in enumerate(plaintext)
        ])
        encoded = base64.b64encode(encrypted_bytes).decode('utf-8')

        result = xor_decipher(encoded, key)
        assert result == plaintext

    def test_xor_decipher_invalid_base64(self):
        """Retourne chaîne vide si base64 invalide."""
        result = xor_decipher("not-valid-base64!!!", "key")
        assert result == ""

    def test_xor_decipher_empty_string(self):
        """Gère une chaîne vide."""
        result = xor_decipher("", "key")
        assert result == ""


class TestExtractContextFromUrl:
    """Tests d'extraction du contexte depuis l'URL."""

    def test_extract_full_context(self):
        """Extrait tous les paramètres d'une URL complète."""
        url = "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/18-ans-f-2e-division-28369/poule-179943/journee-5/"

        result = _extract_context_from_url(url)

        assert result['ext_saison_id'] == '21'
        assert result['url_competition_type'] == 'regional'
        assert result['url_competition'] == '18-ans-f-2e-division-28369'
        assert result['ext_poule_id'] == '179943'
        assert result['numero_journee'] == '5'

    def test_extract_without_journee(self):
        """Fonctionne sans numéro de journée."""
        url = "https://www.ffhandball.fr/competitions/saison-2025-2026-21/departemental/championnat-13-feminins-28964/poule-175593/classements/"

        result = _extract_context_from_url(url)

        assert result['ext_saison_id'] == '21'
        assert result['url_competition_type'] == 'departemental'
        assert result['ext_poule_id'] == '175593'
        assert 'numero_journee' not in result

    def test_extract_minimal_url(self):
        """Gère une URL minimale."""
        url = "https://www.ffhandball.fr/competitions/"

        result = _extract_context_from_url(url)

        assert result == {}


class TestFindRankingBlockName:
    """Tests de détection du nom de bloc ranking."""

    def test_finds_ranking_component(self):
        """Trouve un composant avec 'ranking' dans le nom."""
        from bs4 import BeautifulSoup
        html = '''
        <html>
            <smartfire-component name="header"></smartfire-component>
            <smartfire-component name="competitions-ranking-table"></smartfire-component>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')

        result = _find_ranking_block_name(soup)

        assert result == "competitions-ranking-table"

    def test_finds_classement_component(self):
        """Trouve un composant avec 'classement' dans le nom."""
        from bs4 import BeautifulSoup
        html = '''
        <html>
            <smartfire-component name="classement-poule"></smartfire-component>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')

        result = _find_ranking_block_name(soup)

        assert result == "classement-poule"

    def test_returns_default_if_not_found(self):
        """Retourne le nom par défaut si aucun composant trouvé."""
        from bs4 import BeautifulSoup
        html = '<html><smartfire-component name="other"></smartfire-component></html>'
        soup = BeautifulSoup(html, 'html.parser')

        result = _find_ranking_block_name(soup)

        assert result == "competitions---new-competition-phase-ranking"


class TestGetRankingFromApi:
    """Tests de la fonction principale d'orchestration."""

    @pytest.fixture
    def mock_html_page(self):
        """Page HTML simulée avec data-cfk."""
        return '''
        <html>
            <head><title>-18 Ans M 2e Division - Classement - FFHandball</title></head>
            <body data-cfk="secretkey123">
                <smartfire-component name="ranking-block"></smartfire-component>
            </body>
        </html>
        '''

    @pytest.fixture
    def mock_api_response(self):
        """Réponse API simulée (avant chiffrement)."""
        return {
            "title": "-18 Ans M 2e Division",
            "ranking": [
                {"teamName": "Club A", "rank": 1, "points": 15, "won": 5, "lost": 0, "draws": 0},
                {"teamName": "Club B", "rank": 2, "points": 12, "won": 4, "lost": 1, "draws": 0},
            ]
        }

    def _encrypt_response(self, data: dict, key: str) -> str:
        """Chiffre une réponse pour le mock."""
        import json
        plaintext = json.dumps(data)
        encrypted_bytes = bytes([
            ord(c) ^ ord(key[i % len(key)])
            for i, c in enumerate(plaintext)
        ])
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    def test_successful_fetch(self, mock_html_page, mock_api_response):
        """Test du flux complet avec succès."""
        key = "secretkey123"
        encrypted = self._encrypt_response(mock_api_response, key)

        with patch('src.scraping.get_ranking_api.requests.Session') as MockSession, \
             patch('src.scraping.get_ranking_api.get_rate_limiter') as mock_limiter:

            mock_session = MagicMock()
            MockSession.return_value = mock_session

            # Mock du rate limiter
            mock_limiter.return_value.wait = MagicMock()

            # Mock des réponses HTTP
            html_response = MagicMock()
            html_response.text = mock_html_page
            html_response.raise_for_status = MagicMock()

            api_response = MagicMock()
            api_response.status_code = 200
            api_response.json.return_value = encrypted

            mock_session.get.side_effect = [html_response, api_response]

            # Appel
            url = "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/test/poule-123/classements/"
            title, ranking = get_ranking_from_api(url)

            # Vérifications
            assert title == "-18 Ans M 2e Division"
            assert len(ranking) == 2
            assert ranking[0]['team_name'] == "Club A"
            assert ranking[0]['rank'] == 1
            assert ranking[0]['points'] == 15

    def test_missing_data_cfk(self):
        """Retourne vide si data-cfk manquant."""
        html_without_key = '<html><body></body></html>'

        with patch('src.scraping.get_ranking_api.requests.Session') as MockSession, \
             patch('src.scraping.get_ranking_api.get_rate_limiter') as mock_limiter:

            mock_session = MagicMock()
            MockSession.return_value = mock_session
            mock_limiter.return_value.wait = MagicMock()

            response = MagicMock()
            response.text = html_without_key
            response.raise_for_status = MagicMock()
            mock_session.get.return_value = response

            title, ranking = get_ranking_from_api("https://example.com/page")

            assert title is None
            assert ranking == []

    def test_api_error_status(self, mock_html_page):
        """Gère les erreurs HTTP de l'API."""
        with patch('src.scraping.get_ranking_api.requests.Session') as MockSession, \
             patch('src.scraping.get_ranking_api.get_rate_limiter') as mock_limiter:

            mock_session = MagicMock()
            MockSession.return_value = mock_session
            mock_limiter.return_value.wait = MagicMock()

            html_response = MagicMock()
            html_response.text = mock_html_page
            html_response.raise_for_status = MagicMock()

            api_response = MagicMock()
            api_response.status_code = 500

            mock_session.get.side_effect = [html_response, api_response]

            title, ranking = get_ranking_from_api("https://example.com/poule-123/classements/")

            assert title is None
            assert ranking == []

    def test_decryption_failure(self, mock_html_page):
        """Gère l'échec du déchiffrement."""
        with patch('src.scraping.get_ranking_api.requests.Session') as MockSession, \
             patch('src.scraping.get_ranking_api.get_rate_limiter') as mock_limiter:

            mock_session = MagicMock()
            MockSession.return_value = mock_session
            mock_limiter.return_value.wait = MagicMock()

            html_response = MagicMock()
            html_response.text = mock_html_page
            html_response.raise_for_status = MagicMock()

            api_response = MagicMock()
            api_response.status_code = 200
            api_response.json.return_value = "invalid-not-base64!!!"

            mock_session.get.side_effect = [html_response, api_response]

            title, ranking = get_ranking_from_api("https://example.com/poule-123/classements/")

            assert title is None
            assert ranking == []

    def test_title_fallback_from_html(self, mock_html_page):
        """Utilise le titre HTML si absent de l'API."""
        key = "secretkey123"
        # Réponse API sans titre
        api_data = {"ranking": [{"teamName": "Club", "rank": 1, "points": 10}]}
        encrypted = self._encrypt_response(api_data, key)

        with patch('src.scraping.get_ranking_api.requests.Session') as MockSession, \
             patch('src.scraping.get_ranking_api.get_rate_limiter') as mock_limiter:

            mock_session = MagicMock()
            MockSession.return_value = mock_session
            mock_limiter.return_value.wait = MagicMock()

            html_response = MagicMock()
            html_response.text = mock_html_page
            html_response.raise_for_status = MagicMock()

            api_response = MagicMock()
            api_response.status_code = 200
            api_response.json.return_value = encrypted

            mock_session.get.side_effect = [html_response, api_response]

            title, ranking = get_ranking_from_api("https://example.com/poule-123/classements/")

            # Fallback sur le titre HTML
            assert title == "-18 Ans M 2e Division"

    def test_network_exception_handling(self):
        """Gère les exceptions réseau."""
        import requests

        with patch('src.scraping.get_ranking_api.requests.Session') as MockSession, \
             patch('src.scraping.get_ranking_api.get_rate_limiter') as mock_limiter:

            mock_session = MagicMock()
            MockSession.return_value = mock_session
            mock_limiter.return_value.wait = MagicMock()

            mock_session.get.side_effect = requests.exceptions.ConnectionError("Network down")

            title, ranking = get_ranking_from_api("https://example.com/page")

            assert title is None
            assert ranking == []

    def test_poule_id_fallback(self, mock_html_page, mock_api_response):
        """Utilise le poule_id_fallback si absent de l'URL."""
        key = "secretkey123"
        encrypted = self._encrypt_response(mock_api_response, key)

        with patch('src.scraping.get_ranking_api.requests.Session') as MockSession, \
             patch('src.scraping.get_ranking_api.get_rate_limiter') as mock_limiter:

            mock_session = MagicMock()
            MockSession.return_value = mock_session
            mock_limiter.return_value.wait = MagicMock()

            html_response = MagicMock()
            html_response.text = mock_html_page
            html_response.raise_for_status = MagicMock()

            api_response = MagicMock()
            api_response.status_code = 200
            api_response.json.return_value = encrypted

            mock_session.get.side_effect = [html_response, api_response]

            # URL sans poule-ID, mais fallback fourni
            url = "https://www.ffhandball.fr/competitions/saison-2025-2026-21/regional/test/classements/"
            title, ranking = get_ranking_from_api(url, poule_id_fallback="99999")

            assert title is not None
            assert len(ranking) == 2
