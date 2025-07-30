"""
Custom exceptions for the GeoIP API package.
"""


class GeoIPError(Exception):
    """Base exception for all GeoIP API errors."""

    pass


class DatabaseError(GeoIPError):
    """Raised when there is an error with the database."""

    pass


class InvalidIPError(GeoIPError):
    """Raised when an invalid IP address is provided."""

    pass


class LookupError(GeoIPError):
    """Raised when a lookup operation fails."""

    pass
