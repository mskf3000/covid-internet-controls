import logging
import socket

log = logging.getLogger(__name__)


def ip_lookup(hostname: str) -> str:
    """
    Lookup an IP address for a given hostname.
    :param hostname: host to look up
    :return: IP address string
    """

    host_ip = ""

    if not hostname:
        return host_ip

    try:
        host_ip = socket.gethostbyname(hostname)

    except socket.error:
        log.debug(f"Unable to lookup IP address for {hostname}.")

    except Exception as e:
        log.error(
            f"Unknown exception occurred when looking up IP address for {hostname}: {e}"
        )

    finally:
        return host_ip
