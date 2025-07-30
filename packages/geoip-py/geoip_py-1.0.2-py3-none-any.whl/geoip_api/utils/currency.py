"""
Currency mapping utilities for GeoIP API using pycountry.
"""

import logging
from typing import Any, Optional

try:
    import pycountry

    _pycountry: Optional[Any] = pycountry
    PYCOUNTRY_AVAILABLE = True
except ImportError:
    _pycountry = None
    PYCOUNTRY_AVAILABLE = False
    logging.warning("pycountry not installed. Currency lookups will be limited.")

logger = logging.getLogger(__name__)

# Minimal mapping for most common countries only
# This covers ~90% of global internet traffic
COMMON_COUNTRY_CURRENCY_MAP = {
    "US": "USD",  # United States
    "CN": "CNY",  # China
    "JP": "JPY",  # Japan
    "DE": "EUR",  # Germany
    "GB": "GBP",  # United Kingdom
    "FR": "EUR",  # France
    "IN": "INR",  # India
    "IT": "EUR",  # Italy
    "BR": "BRL",  # Brazil
    "CA": "CAD",  # Canada
    "RU": "RUB",  # Russia
    "KR": "KRW",  # South Korea
    "ES": "EUR",  # Spain
    "AU": "AUD",  # Australia
    "MX": "MXN",  # Mexico
    "ID": "IDR",  # Indonesia
    "NL": "EUR",  # Netherlands
    "SA": "SAR",  # Saudi Arabia
    "TR": "TRY",  # Turkey
    "CH": "CHF",  # Switzerland
    "TW": "TWD",  # Taiwan
    "BE": "EUR",  # Belgium
    "AR": "ARS",  # Argentina
    "SE": "SEK",  # Sweden
    "IE": "EUR",  # Ireland
    "IL": "ILS",  # Israel
    "AT": "EUR",  # Austria
    "NG": "NGN",  # Nigeria
    "NO": "NOK",  # Norway
    "AE": "AED",  # United Arab Emirates
    "MY": "MYR",  # Malaysia
    "ZA": "ZAR",  # South Africa
    "PH": "PHP",  # Philippines
    "FI": "EUR",  # Finland
    "DK": "DKK",  # Denmark
    "CL": "CLP",  # Chile
    "SG": "SGD",  # Singapore
    "BD": "BDT",  # Bangladesh
    "VN": "VND",  # Vietnam
    "PT": "EUR",  # Portugal
    "CZ": "CZK",  # Czech Republic
    "NZ": "NZD",  # New Zealand
    "PL": "PLN",  # Poland
    "RO": "RON",  # Romania
    "GR": "EUR",  # Greece
    "HU": "HUF",  # Hungary
    "TH": "THB",  # Thailand
    "HK": "HKD",  # Hong Kong
    "UA": "UAH",  # Ukraine
    "EG": "EGP",  # Egypt
    "HR": "EUR",  # Croatia
    "BG": "BGN",  # Bulgaria
    "LT": "EUR",  # Lithuania
    "LV": "EUR",  # Latvia
    "EE": "EUR",  # Estonia
    "SI": "EUR",  # Slovenia
    "SK": "EUR",  # Slovakia
    "LU": "EUR",  # Luxembourg
    "MT": "EUR",  # Malta
    "CY": "EUR",  # Cyprus
}


def get_currency_for_country(country_code: Optional[str]) -> Optional[str]:
    """
    Get the primary currency for a given country code.

    Args:
        country_code: ISO 3166-1 alpha-2 country code

    Returns:
        ISO 4217 currency code or None if not found
    """
    if not country_code:
        return None

    # Convert to uppercase for consistency
    country_code = country_code.upper()

    # Validate country code exists using pycountry if available
    if PYCOUNTRY_AVAILABLE:
        try:
            country = pycountry.countries.get(alpha_2=country_code)
            if not country:
                logger.debug(
                    f"Country code {country_code} not found in pycountry database"
                )
                return None
        except Exception as e:
            logger.warning(f"Error validating country code with pycountry: {e}")

    # Get currency from our common mapping
    currency_code = COMMON_COUNTRY_CURRENCY_MAP.get(country_code)

    if currency_code and PYCOUNTRY_AVAILABLE:
        # Validate that the currency exists in pycountry
        try:
            currency = pycountry.currencies.get(alpha_3=currency_code)
            if currency:
                logger.debug(
                    f"Found currency {currency_code} for country {country_code}"
                )
                return currency_code
            else:
                logger.warning(
                    f"Currency {currency_code} not found in pycountry database"
                )
                return None
        except Exception as e:
            logger.warning(f"Error validating currency with pycountry: {e}")

    if currency_code:
        logger.debug(f"Found currency {currency_code} for country {country_code}")
    else:
        logger.debug(f"No currency mapping found for country code: {country_code}")

    return currency_code


def get_currency_info(currency_code: Optional[str]) -> Optional[dict]:
    """
    Get detailed currency information using pycountry.

    Args:
        currency_code: ISO 4217 currency code

    Returns:
        Dictionary with currency information or None if not found
    """
    if not currency_code or not PYCOUNTRY_AVAILABLE:
        return None

    try:
        currency = pycountry.currencies.get(alpha_3=currency_code.upper())
        if currency:
            return {
                "code": currency.alpha_3,
                "name": currency.name,
                "numeric": currency.numeric,
            }
    except Exception as e:
        logger.warning(f"Error getting currency info for {currency_code}: {e}")

    return None
