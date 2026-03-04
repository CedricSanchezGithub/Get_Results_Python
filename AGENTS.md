# AGENTS.md - Developer Guide for AI Agents

This file provides guidance for AI coding agents working in this FFHandball Scraper repository.

## Project Overview

FFHandball Scraper is a Python data acquisition module that scrapes match results and rankings from the French Handball Federation website. It uses secure API calls with XOR decryption for rankings and HTML parsing for match data.

---

## Build, Lint & Test Commands

### Running Tests

```bash
# Run all tests (51 tests)
pytest

# Run a single test file
pytest tests/test_api_client.py

# Run tests by name pattern
pytest -k "test_retry"

# Run with verbose output and short traceback
pytest -v --tb=short

# Run a specific test function
pytest tests/test_api_client.py::TestIngestClientRetry::test_retry_on_500_error

# Run with coverage (if installed)
pytest --cov=src --cov-report=term-missing
```

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run scraper manually
python run_daily_scraping.py

# Run with scheduler (Flask + APScheduler)
python scraping_scheduler.py
```

### Docker

```bash
docker build -t getresultscraper .
docker run --env-file .env getresultscraper
```

---

## Code Style Guidelines

### Imports

Group imports in the following order with blank lines between groups:

1. Standard library (`logging`, `re`, `typing`)
2. Third-party packages (`requests`, `pydantic`, `pytest`)
3. Local application imports (`from src.models...`, `from src.scraping...`)

```python
# Good
import logging
from typing import List, Dict, Tuple, Optional

import requests
from pydantic import BaseModel, Field

from src.models.models import MatchIngest, RankingIngest
from src.saving.api_client import IngestClient
```

### Type Hints

- Use the `typing` module for complex types: `List`, `Dict`, `Tuple`, `Optional`, `Callable`
- Use Python 3.10+ union syntax sparingly (stick with `Optional[X]` for compatibility)
- Always add return types to functions

```python
# Good
def _extract_poule_id(url: str) -> Optional[str]:
    match = re.search(r'poule-(\d+)', url)
    return match.group(1) if match else None

def get_all(url_start: str, category: str) -> None:
    ...

# Good - type hint for dict
def _map_to_ingest_model(raw_match: Dict, category: str, pool_id: str) -> Optional[MatchIngest]:
    ...
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Functions/variables | snake_case | `get_all()`, `ingest_client` |
| Classes | PascalCase | `MatchIngest`, `IngestClient` |
| Constants | UPPER_SNAKE | `MAX_RETRIES`, `DEFAULT_DELAY` |
| Private functions | leading underscore | `_extract_poule_id()` |

### Pydantic Models

Use Pydantic v2 for data validation. Define models in `src/models/models.py`:

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class MatchIngest(BaseModel):
    match_date: datetime
    team_1_name: str
    team_1_score: Optional[int] = None
    category: str = Field(..., description="Clé de pivot pour le backend")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%dT%H:%M:%S')
        }
```

### Error Handling

- Use try/except for expected failures that should be logged and skipped
- Log warnings for invalid data that is gracefully handled
- Let unexpected exceptions propagate when appropriate
- Never expose secrets in error messages

```python
# Good - graceful handling with logging
def _map_to_ingest_model(raw_match: Dict, category: str, pool_id: str) -> Optional[MatchIngest]:
    try:
        return MatchIngest(
            match_date=raw_match['match_date'],
            team_1_name=raw_match['team_1_name'],
            ...
        )
    except Exception as e:
        logger.warning(f"⚠️ Donnée invalide ignorée : {e} | Data: {raw_match}")
        return None
```

### Logging

- Use module-level loggers: `logger = logging.getLogger(__name__)`
- Use appropriate log levels: `DEBUG` for development, `INFO` for normal flow, `WARNING` for recoverable issues, `ERROR` for failures

```python
import logging

logger = logging.getLogger(__name__)

def get_all(url_start: str, category: str):
    logger.info(f"🚀 [Start] Scraping '{category}' via {url_start}")
    # ... work ...
    logger.info(f"🏁 [End] Scraping terminé pour '{category}'")
```

### Configuration

All configuration goes through Pydantic Settings in `src/settings.py`. Never use raw `os.environ`:

```python
# Good - use the settings module
from src.settings import get_settings, get_db_settings, get_scraper_settings

settings = get_settings()
db = get_db_settings()
scraper = get_scraper_settings()

# Access values
api_url = settings.backend_api_url
```

### Thread Safety

The scraper uses parallel workers via `ThreadPoolExecutor`. When modifying shared state:

- Use thread-safe singletons like `RateLimiter`
- Avoid mutable global state
- Pass dependencies explicitly where possible

```python
# Rate limiter is a thread-safe singleton
from src.utils.rate_limiter import RateLimiter

limiter = RateLimiter()  # Gets the shared instance
```

### Testing Guidelines

Follow these patterns for writing tests:

1. Use pytest fixtures for setup
2. Use `unittest.mock` for external dependencies
3. Group tests in classes by functionality
4. Use descriptive test names: `test_<method>_<expected_behavior>`

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def ingest_client():
    with patch.dict("os.environ", {
        "BACKEND_API_URL": "http://test-api/ingest",
        "BACKEND_API_KEY": "test-key"
    }):
        return IngestClient(max_retries=3, base_delay=0.01)


class TestIngestClientRetry:
    def test_retry_on_500_error(self, ingest_client, sample_matches):
        with patch.object(ingest_client.session, 'post') as mock_post:
            mock_post.side_effect = [
                MagicMock(status_code=500),
                MagicMock(status_code=200)
            ]
            result = ingest_client.send_matches(sample_matches)
            assert result is True
            assert mock_post.call_count == 2
```

### File Organization

```
src/
├── config.py           # Path constants (BASE_DIR, LOGS_DIR)
├── settings.py         # Pydantic Settings (config validation)
├── scraping/           # Data extraction
│   ├── get_all.py      # Main orchestrator
│   ├── get_match_results.py
│   ├── get_ranking_api.py
│   └── get_ranking.py
├── saving/             # Data ingestion
│   ├── api_client.py   # IngestClient
│   └── db_logger.py    # Audit logging
├── database/           # DB connection
├── models/             # Pydantic models
│   └── models.py
└── utils/              # Utilities
    ├── rate_limiter.py
    ├── format_date.py
    └── logging_config.py
tests/
├── test_*.py
```

---

## Key Patterns

### Retry with Exponential Backoff

The `IngestClient` retries 3 times with exponential backoff (1s → 2s → 4s):
- 5xx errors trigger retry
- Network errors trigger retry
- 4xx errors fail immediately

### Rate Limiting

All HTTP requests to FFHandball use the global `RateLimiter` singleton:
- Default: 1s minimum delay between requests
- Burst limit: 10 requests per 15s window
- Thread-safe for parallel workers

### Partial Success

Individual source failures don't stop the job. The scraper continues processing other competitions and marks the overall job status as `PARTIAL_SUCCESS` if some sources fail.

---

## Environment Variables

Required variables (see `.env.example`):

```ini
# Database
MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

# Backend API (data ingestion)
BACKEND_API_URL, BACKEND_API_KEY

# Source API (competition list)
API_URL, API_KEY

# Optional tuning
SCRAPER_MAX_WORKERS=3
SCRAPER_RATE_LIMIT_DELAY=1.0
SCRAPER_REQUEST_TIMEOUT=15
LOG_LEVEL=INFO
DEBUG=false
```
