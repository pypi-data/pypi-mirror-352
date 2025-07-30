"""
Database management for GeoIP API.
"""

import logging
import os
import shutil
from pathlib import Path

import requests

from geoip_api.config import (
    ASN_DB_URL,
    CITY_DB_URL,
    DEFAULT_ASN_DB_PATH,
    DEFAULT_CITY_DB_PATH,
    DOWNLOAD_TIMEOUT,
)
from geoip_api.exceptions import DatabaseError

logger = logging.getLogger(__name__)


def ensure_db_dir(db_path):
    """Ensure the database directory exists."""
    db_dir = Path(db_path).parent
    if not db_dir.exists():
        logger.info(f"Creating database directory: {db_dir}")
        db_dir.mkdir(parents=True, exist_ok=True)


def download_database(url, target_path):
    """
    Download a database file from the specified URL.

    Args:
        url: Source URL for the database
        target_path: Path where the database should be saved

    Returns:
        Path to the downloaded database

    Raises:
        DatabaseError: If download fails
    """
    logger.info(f"Downloading database from {url} to {target_path}")
    ensure_db_dir(target_path)

    try:
        response = requests.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT)
        response.raise_for_status()

        with open(target_path, "wb") as f:
            shutil.copyfileobj(response.raw, f)

        logger.info(f"Successfully downloaded database to {target_path}")
        return target_path

    except (requests.RequestException, IOError) as e:
        logger.error(f"Failed to download database: {e}")
        raise DatabaseError(f"Failed to download database: {e}") from e


def get_database_path(db_type="city", download_if_missing=False):
    """
    Get the path to a database file, optionally downloading it if missing.

    Args:
        db_type: Type of database ('city' or 'asn')
        download_if_missing: Whether to download the database if it doesn't exist

    Returns:
        Path to the database file

    Raises:
        ValueError: If an invalid db_type is provided
        DatabaseError: If the database is missing and download_if_missing is False
    """
    if db_type.lower() == "city":
        db_path = DEFAULT_CITY_DB_PATH
        db_url = CITY_DB_URL
    elif db_type.lower() == "asn":
        db_path = DEFAULT_ASN_DB_PATH
        db_url = ASN_DB_URL
    else:
        raise ValueError(f"Invalid database type: {db_type}. Must be 'city' or 'asn'")

    if not os.path.exists(db_path):
        if download_if_missing:
            return download_database(db_url, db_path)
        else:
            raise DatabaseError(f"Database file not found at {db_path}")

    return db_path
