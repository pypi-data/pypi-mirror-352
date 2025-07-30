"""
Configuration settings for the GeoIP API package.
"""

import os
from pathlib import Path

# Default database paths
DEFAULT_ASN_DB_PATH = os.environ.get(
    "GEOIP_ASN_DB_PATH", str(Path.home() / ".geoip_api" / "GeoLite2-ASN.mmdb")
)
DEFAULT_CITY_DB_PATH = os.environ.get(
    "GEOIP_CITY_DB_PATH", str(Path.home() / ".geoip_api" / "GeoLite2-City.mmdb")
)

# Database download URLs
ASN_DB_URL = "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-ASN.mmdb"
CITY_DB_URL = "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb"

# Download settings
DOWNLOAD_TIMEOUT = 60  # seconds
