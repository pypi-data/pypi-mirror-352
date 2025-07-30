"""
GeoIP lookup functionality with continent support.
"""

import ipaddress
import logging
from typing import Any, Dict, Optional

import geoip2.database
from geoip2.errors import AddressNotFoundError

from geoip_api.core.database import get_database_path
from geoip_api.exceptions import InvalidIPError, LookupError
from geoip_api.utils.currency import get_currency_for_country

logger = logging.getLogger(__name__)


class GeoIPLookup:
    """
    GeoIP lookup service.

    This class provides functionality to look up geolocation information for IP addresses
    using MaxMind's GeoIP2 databases.
    """

    def __init__(
        self,
        city_db_path: Optional[str] = None,
        asn_db_path: Optional[str] = None,
        download_if_missing: bool = False,
    ):
        """
        Initialize the GeoIP lookup service.

        Args:
            city_db_path: Path to the GeoLite2 City database
            asn_db_path: Path to the GeoLite2 ASN database
            download_if_missing: Whether to download databases if they're missing
        """
        self.city_db_path = city_db_path or get_database_path(
            "city", download_if_missing=download_if_missing
        )
        self.asn_db_path = asn_db_path or get_database_path(
            "asn", download_if_missing=download_if_missing
        )
        logger.debug(
            f"Initialized GeoIPLookup with city_db={self.city_db_path}, asn_db={self.asn_db_path}"
        )

    def validate_ip(self, ip_address: str) -> None:
        """
        Validate that the provided string is a valid IP address.

        Args:
            ip_address: IP address to validate

        Raises:
            InvalidIPError: If the IP address is invalid
        """
        try:
            ipaddress.ip_address(ip_address)
        except ValueError as e:
            logger.warning(f"Invalid IP address: {ip_address}")
            raise InvalidIPError(f"Invalid IP address: {ip_address}") from e

    def lookup(self, ip_address: str) -> Dict[str, Any]:
        """
        Look up geolocation information for an IP address.

        Args:
            ip_address: IP address to look up

        Returns:
            Dictionary containing geolocation information

        Raises:
            InvalidIPError: If the IP address is invalid
            LookupError: If the lookup fails
        """
        self.validate_ip(ip_address)

        try:
            logger.info(f"Looking up IP address: {ip_address}")
            geo_details = {}

            # Get city information
            with geoip2.database.Reader(self.city_db_path) as city_reader:
                try:
                    city_response = city_reader.city(ip_address)
                    country_code = city_response.country.iso_code
                    geo_details.update(
                        {
                            "code": country_code,
                            "country": city_response.country.name,
                            "continent": city_response.continent.name,
                            "continent_code": city_response.continent.code,
                            "city": city_response.city.name,
                            "lat": city_response.location.latitude,
                            "lon": city_response.location.longitude,
                            "tz": city_response.location.time_zone,
                        }
                    )

                    # Add currency information
                    currency_code = get_currency_for_country(country_code)
                    geo_details["currency"] = currency_code

                except AddressNotFoundError:
                    logger.warning(f"City information not found for IP: {ip_address}")
                    geo_details.update(
                        {
                            "code": None,
                            "country": None,
                            "continent": None,
                            "continent_code": None,
                            "city": None,
                            "lat": None,
                            "lon": None,
                            "tz": None,
                            "currency": None,
                        }
                    )

            # Get ASN information
            with geoip2.database.Reader(self.asn_db_path) as asn_reader:
                try:
                    asn_response = asn_reader.asn(ip_address)
                    geo_details.update(
                        {
                            "isp": asn_response.autonomous_system_organization,
                            "asn": asn_response.autonomous_system_number,
                        }
                    )
                except AddressNotFoundError:
                    logger.warning(f"ASN information not found for IP: {ip_address}")
                    geo_details.update({"isp": None, "asn": None})

            logger.info(f"Lookup successful for IP: {ip_address}")
            return geo_details

        except Exception as e:
            logger.error(f"Error looking up IP {ip_address}: {e}")
            raise LookupError(f"Error looking up IP {ip_address}: {e}") from e
