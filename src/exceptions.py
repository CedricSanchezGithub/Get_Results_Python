class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass


class FetchError(ScraperError):
    """Raised when a fetch operation fails."""
    def __init__(self, url: str, message: str = ""):
        self.url = url
        self.message = message
        super().__init__(f"Failed to fetch {url}: {message}" if message else f"Failed to fetch {url}")


class ParseError(ScraperError):
    """Raised when parsing fails."""
    def __init__(self, source: str, message: str = ""):
        self.source = source
        self.message = message
        super().__init__(f"Failed to parse {source}: {message}" if message else f"Failed to parse {source}")


class APIError(ScraperError):
    """Raised when API call fails."""
    def __init__(self, endpoint: str, status_code: int = None, message: str = ""):
        self.endpoint = endpoint
        self.status_code = status_code
        self.message = message
        msg = f"API error for {endpoint}"
        if status_code:
            msg += f" (status: {status_code})"
        if message:
            msg += f": {message}"
        super().__init__(msg)


class DecryptionError(ScraperError):
    """Raised when XOR decryption fails."""
    def __init__(self, message: str = "Decryption failed"):
        self.message = message
        super().__init__(message)


class RateLimitError(ScraperError):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str = "Rate limit exceeded"):
        self.message = message
        super().__init__(message)


class ConfigurationError(ScraperError):
    """Raised when configuration is invalid."""
    def __init__(self, setting: str, message: str = ""):
        self.setting = setting
        self.message = message
        msg = f"Invalid configuration for {setting}"
        if message:
            msg += f": {message}"
        super().__init__(msg)


class IngestError(ScraperError):
    """Raised when data ingestion fails."""
    def __init__(self, message: str = "Ingestion failed", status_code: int = None):
        self.status_code = status_code
        super().__init__(f"{message} (status: {status_code})" if status_code else message)
