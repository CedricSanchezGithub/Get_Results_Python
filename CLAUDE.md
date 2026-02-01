# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FFHandball Scraper is a Python data acquisition module that scrapes match results and rankings from the official FFHandball (French Handball Federation) website. It uses a **multi-source strategy**: secure API calls with XOR decryption for rankings, and HTML parsing for match data.

## Commands

```bash
# Run scraper manually
python run_daily_scraping.py

# Run with scheduler (Flask + APScheduler, daily at 00:00 UTC)
python scraping_scheduler.py

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest                           # All tests (51 tests)
pytest tests/test_api_client.py  # Single file
pytest -k "test_retry"           # By name pattern
pytest -v --tb=short             # Verbose with short traceback

# Docker
docker build -t getresultscraper .
docker run --env-file .env getresultscraper
```

## Project Structure

```
├── run_daily_scraping.py      # Entry point (parallel scraping)
├── scraping_scheduler.py      # Flask scheduler service
├── src/
│   ├── settings.py            # Pydantic Settings (config validation)
│   ├── config.py              # Path constants (BASE_DIR, LOGS_DIR)
│   ├── scraping/
│   │   ├── get_all.py         # Main orchestrator
│   │   ├── get_match_results.py  # HTML scraper
│   │   ├── get_ranking_api.py    # XOR decryption + API
│   │   └── get_ranking.py     # Ranking parser
│   ├── saving/
│   │   ├── api_client.py      # IngestClient (retry + backoff)
│   │   └── db_logger.py       # Audit logging (scraping_log table)
│   ├── database/
│   │   └── db_connector.py    # MySQL connection
│   ├── models/
│   │   └── models.py          # Pydantic MatchIngest
│   └── utils/
│       ├── rate_limiter.py    # Thread-safe rate limiting
│       ├── format_date.py     # Date parsing (ISO + French)
│       └── logging_config.py  # Rotating file logger
├── tests/                     # Pytest suite
├── scripts/                   # Debug & utility scripts
└── requirements.txt           # Direct dependencies only
```

## Architecture

### Data Flow

```
run_daily_scraping.py (ThreadPoolExecutor)
    │
    ├─→ get_urls_from_api()          # Fetch competition list
    │
    └─→ [Parallel workers] ──→ get_all() per competition
                                  │
                                  ├─→ get_ranking_from_api()
                                  │     ├─ Fetch HTML for data-cfk key
                                  │     ├─ Call /wp-json API
                                  │     └─ XOR decrypt response
                                  │
                                  ├─→ get_matches_from_url()
                                  │     ├─ fetch_html() with rate limiting
                                  │     └─ Parse smartfire-component JSON
                                  │
                                  └─→ IngestClient.send_matches()
                                        └─ POST with retry + exponential backoff
```

### Key Components

| Module | Purpose |
|--------|---------|
| `src/settings.py` | Pydantic Settings - validated config from `.env` |
| `src/scraping/get_all.py` | Main orchestrator with pagination |
| `src/scraping/get_ranking_api.py` | XOR decryption for encrypted API |
| `src/saving/api_client.py` | `IngestClient` with retry (3 attempts, backoff) |
| `src/utils/rate_limiter.py` | Thread-safe singleton rate limiter |
| `src/utils/format_date.py` | Robust date parsing (ISO + French text) |
| `src/models/models.py` | Pydantic `MatchIngest` model |

### Why XOR Decryption?

The FFHandball API returns ranking data with XOR+Base64 obfuscation. The `get_ranking_api.py` module decrypts this to extract the **official_phase_name** (e.g., "Excellence" vs "Brassage"), which is critical for distinguishing competition phases in the UI.

## Configuration

All configuration uses **Pydantic Settings** (`src/settings.py`) with automatic `.env` loading and validation.

```python
from src.settings import get_settings, get_db_settings, get_scraper_settings

settings = get_settings()
db = get_db_settings()
scraper = get_scraper_settings()
```

### Environment Variables

```ini
# Database (required)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_DATABASE=get_results

# Backend API - data ingestion (required)
BACKEND_API_URL=http://backend:8081/api/ingest/matches
BACKEND_API_KEY=your_api_key

# Source API - competition list (required)
API_URL=http://backend:8081/api/competitions
API_KEY=secret_key

# Scraper tuning (optional, with defaults)
SCRAPER_MAX_WORKERS=3            # Parallel workers (1-10)
SCRAPER_RATE_LIMIT_DELAY=1.0     # Min delay between requests (0.1-10s)
SCRAPER_REQUEST_TIMEOUT=15       # HTTP timeout (5-60s)

# Application (optional)
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR, CRITICAL
DEBUG=false
```

## Patterns to Follow

### Error Handling
- **Retry with backoff**: `IngestClient` retries 3 times with exponential backoff (1s → 2s → 4s)
- **Non-retryable errors**: 4xx errors fail immediately, 5xx and network errors trigger retry
- **Partial success**: Individual source failures don't stop the job; status becomes `PARTIAL_SUCCESS`

### Rate Limiting
- All HTTP requests to FFHandball use the global `RateLimiter` singleton
- Default: 1s minimum delay, burst limit of 10 requests per 15s window
- Thread-safe for parallel workers

### Configuration
- Use `src/settings.py` helpers (`get_db_settings()`, etc.)
- Validation happens at startup via Pydantic
- See `.env.example` for all available options

### Data Validation
- Use `MatchIngest` Pydantic model for API payloads
- Polymorphic field mapping: ranking parser handles 20+ field name variations using `.get()` chains

### Database
- Only `scraping_log` table is used directly (audit trail)
- Match/ranking data is sent via API (`IngestClient`), not written to DB
- Connection healthcheck runs once at startup (not per query)

## Testing

Test coverage includes:
- `test_format_date.py` - Date parsing (ISO, French, edge cases)
- `test_models.py` - Pydantic validation and serialization
- `test_api_client.py` - Retry logic, backoff, error handling
- `test_rate_limiter.py` - Thread safety, burst control
- `test_settings.py` - Config validation, defaults, bounds

Run with: `pytest -v`
