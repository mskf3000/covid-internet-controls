from scapy.all import DNS, DNSQR, DNSRR, IP, UDP, sr1


def dns_lookup(ip_address: str) -> str:
    """
    Perform a reverse DNS lookup on a host IP address.
    :param ip_Address: target IP address
    :return: DNS address of provided IP address
    """

    addr = ".".join(ip_address.split(".")[::-1])
    answer = sr1(
        IP(dst="8.8.8.8")
        / UDP(dport=53)
        / DNS(rd=1, qd=DNSQR(qname=f"{addr}.in-addr.arpa", qtype="PTR")),
        verbose=0,
    )
    if answer[DNS].ancount > 0:
        return answer[DNSRR][0].rdata.decode()
