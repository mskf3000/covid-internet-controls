import logging
import os

import geoip2.database
import geoip2.errors

city_reader = geoip2.database.Reader(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "geolite_databases",
        "GeoLite2-City.mmdb",
    )
)

log = logging.getLogger(__name__)


def geolocate(target: str) -> str:
    """
    Get the geolocation of a target IP address, using the Maxmind database.
    https://www.maxmind.com/en/home
    :param target: target IP address
    :return: string containing the {city}, {country}, if found
    """

    location = ""

    if not target:
        return location

    try:
        geolookup = city_reader.city(target)
        if geolookup.country.name:
            location += f"{geolookup.country.name}"

        if geolookup.city.name:
            location += f", {geolookup.city.name}"

    except geoip2.errors.AddressNotFoundError:
        log.debug(f"Address not found for {target}.")

    except Exception as e:
        log.error(f"Unable to geolocate {target}: {e}")

    finally:
        return location
