import logging
import os

import geoip2.database
import geoip2.errors

log = logging.getLogger(__name__)

asn_reader = geoip2.database.Reader(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "geolite_databases",
        "GeoLite2-ASN.mmdb",
    )
)


def asn_lookup(target: str):
    """
    Lookup an IP addresses ASN organization and system number.
    :param target: input IP address
    :return: string containing {system number}:{organization}
    """

    asn = ""

    if not target:
        return asn

    try:
        geolookup = asn_reader.asn(target)
        asn = (
            str(geolookup.autonomous_system_number)
            + ":"
            + geolookup.autonomous_system_organization
        )

    except geoip2.errors.AddressNotFoundError:
        log.debug(f"No ASN found for {target}.")

    except Exception as e:
        log.error(f"Unable to lookup ASN for {target}: {e}")

    finally:
        return asn
