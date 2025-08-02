"""Custom exceptions for the anifiller application."""


class AnifillerError(Exception):
    """Base exception class for anifiller errors."""


class EpisodeInfoNotFoundError(AnifillerError):
    """Raised when episode information is not found on the page."""

    def __init__(self, message: str = "Could not find episode information on the page") -> None:
        super().__init__(message)


class ShowsListNotFoundError(AnifillerError):
    """Raised when shows list is not found on the page."""

    def __init__(self, message: str = "Could not find shows list on the page") -> None:
        super().__init__(message)


class ScrapingError(AnifillerError):
    """Raised when there's an error during web scraping."""

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        super().__init__(message)
        self.original_error = original_error
