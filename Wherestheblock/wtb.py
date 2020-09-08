#!/usr/bin/env python3

import argparse
import json
import logging
import multiprocessing
import os
import socket
import ssl
import sys
import time
import random
from datetime import datetime
from http.client import HTTPResponse
from itertools import repeat

import certifi
import coloredlogs
from fake_useragent import UserAgent
from scapy.all import DNS, DNSQR, ICMP, IP, TCP, UDP, sr1

from utils.asn_lookup import asn_lookup
from utils.csv_utils import read_csv_input_file
from utils.dns_lookup import dns_lookup
from utils.geolocate import geolocate

ca_certs = certifi.where()

logging.getLogger("scapy").setLevel(logging.ERROR)
log = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="%(message)s")
user_agent = UserAgent()


class Traceroute(dict):
    """
    Represents an individual traceroute to a target.
    """

    def __init__(
        self,
        target: str,
        protocol: str = "icmp",
        max_ttl: int = 30,
        timeout: int = 5,
        stealth: bool = False,
    ) -> None:
        self.hops = []
        self.max_ttl = max_ttl
        self.protocol = protocol
        self.target = target
        self.time = str(datetime.now())
        self.timeout = timeout
        self.protocol = protocol
        self.stealth = stealth

        payloads = {
            "icmp": ICMP(),
            "tcp": TCP(dport=53, flags="S"),
            "udp": UDP() / DNS(qd=DNSQR(qname=self.target)),
            "http": TCP(dport=80, flags="S"),
            "tls": TCP(dport=443, flags="S"),
        }
        self.payload = payloads.get(self.protocol)
        self.run()
        return

    def run(self) -> None:
        """
        Run the traceroute to the target, taking into account predetermined
        maximum hop count, protocol, and timeout.
        """

        for ttl in range(1, self.max_ttl + 1):
            try:
                pkt = IP(dst=self.target, ttl=ttl) / self.payload
                reply = sr1(pkt, verbose=0, timeout=self.timeout)

            except socket.gaierror as e:
                log.error(f"Unable to resolve IP for {self.target}: {e}")
                return

            except Exception as e:
                log.error(f"Non-socket exception occured: {e}")
                return

            else:
                # no response, endpoint is likely dropping this traffic
                hop = Hop(ttl=ttl, sent_time=pkt.sent_time)
                if reply is None:
                    hop.source = "*"

                else:
                    hop.source = reply.src
                    hop.reply_time = reply.time

                    if reply.haslayer(ICMP):
                        hop.response = reply.sprintf("%ICMP.type%")

                    else:
                        # if we received a response back that is not ICMP,
                        # we likely received back a SYN/ACK for an HTTP request.

                        if self.protocol == "http" or self.protocol == "tls":

                            # build the http request
                            request_body = "\r\n".join(
                                [
                                    f"GET / HTTP/1.1",
                                    f"Host: {self.target}",
                                    f"User-Agent: {user_agent.random}",
                                    f"Connection: keep-alive",
                                    f"Cache-Control: no-store",
                                    f"Accept: text/html",
                                    f"\r\n",
                                ]
                            ).encode()

                            # create the initial socket
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            sock.settimeout(self.timeout)

                            if self.protocol == "tls":
                                port = 443

                                # wrap the socket with TLS, requiring a certificate
                                # and matching the cert with the certifi database
                                sock = ssl.wrap_socket(
                                    sock,
                                    ssl_version=ssl.PROTOCOL_TLSv1,
                                    cert_reqs=ssl.CERT_REQUIRED,
                                    ca_certs=ca_certs,
                                )

                            else:
                                port = 80

                            sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
                            hop.sent_time = time.time()

                            try:
                                sock.connect((self.target, port))
                                sock.sendall(request_body)

                            except socket.error as e:
                                # no response or some other type of error
                                hop.source = "*"
                                hop.response = str(e)

                            else:
                                # target hit, record the data
                                hop.reply_time = time.time()
                                response = HTTPResponse(sock)
                                response.begin()
                                results = response.read().decode()
                                hop.response = f"{response.getcode()}: {results}"

                            finally:
                                sock.close()

                # finally, calculate metrics for the hop and add it to our results
                hop.finalize()
                self.hops.append(hop)

                if self.stealth:
                    slt = random.randint(1, 5)
                    log.debug(f"Sleeping for {slt}...")
                    time.sleep(slt)

        self.write_results()

    def write_results(self) -> None:
        """
        Write results out to a JSON file. Additionally, receive the multiprocessing
        lock and write out our results to stdout.
        """
        filename = os.path.join("output", self.target + ".json")

        # acquire the lock so we do not garble up output on stdout
        # for multiple targets
        lock.acquire()
        log.info(
            (
                f"\033[1m"
                f"{'TTL':<5} "
                f"{'IP':<20} "
                f"{'DNS':<40} "
                f"{'GEOLOCATION':<35} "
                f"{'ASN':<20} "
                f"{'RTT':<8} "
                f"{'RESPONSE':<15} "
                f"\033[0m"
            )
        )
        for hop in self.hops:
            log.info(hop)
        log.info(f"\033[1mWriting results to {filename}...\033[0m")
        lock.release()

        # rewrite the hop list as dictionaries (maybe this can be done more elegantly)
        self.hops = [vars(hop) for hop in self.hops]

        os.makedirs("output", exist_ok=True)

        results = {
            "hops": self.hops,
            "max_ttl": self.max_ttl,
            "timeout": self.timeout,
            "time": self.time,
        }

        # if we have no output file already existing, we will create one
        if not os.path.exists(filename):
            output = {"url": self.target, "protocol": {self.protocol: []}}
        else:
            # otherwise, we will load it and append the results for this
            # traceroute to the list for the given protocol
            with open(filename, "r") as f:
                output = json.load(f)

            if self.protocol not in output["protocol"].keys():
                output["protocol"][self.protocol] = []

        output["protocol"][self.protocol].append(results)

        with open(filename, "w") as outfile:
            json.dump(output, outfile)


class Hop(dict):
    """
    Represents an individual hop en route to a target.
    """

    def __init__(
        self,
        ttl: int,
        source: str = "",
        sent_time: int = 0,
        reply_time: int = 0,
        response: str = "",
    ) -> None:
        self.source = source
        self.ttl = ttl
        self.sent_time = sent_time
        self.reply_time = reply_time
        self.response = response

    def finalize(self):
        if self.source != "*":
            if self.source not in locations.keys():
                locations[self.source] = geolocate(self.source)

            self.location = locations[self.source]

            if self.source not in asns.keys():
                asns[self.source] = asn_lookup(self.source)

            self.asn = asns[self.source]

            if self.source not in dns_records.keys():
                dns_records[self.source] = dns_lookup(self.source) or ""

            self.dns = dns_records[self.source]

        else:
            self.location = ""
            self.asn = ""
            self.dns = ""

        self.calculate_rtt()

    def calculate_rtt(self):
        """
        Compute the total RTT for a packet.
        :param sent_time: timestamp of packet that was sent
        :param received_time: timestamp of packet that was received
        :return: total RTT in milliseconds
        """
        self.rtt = ""
        if self.sent_time > 0 and self.reply_time > 0:
            try:
                self.rtt = round((self.reply_time - self.sent_time) * 1000, 3)

            except Exception as e:
                log.error(
                    f"Unable to calculate RTT for {self.reply_time} - {self.sent_time}: {e}"
                )

    def __repr__(self):
        return (
            f"{self.ttl:<5} "
            f"{self.source:<20.20} "
            f"{self.dns:<40.40} "
            f"{self.location:<35.35} "
            f"{self.asn:<20.20} "
            f"{self.rtt:<8.8} "
            f"{self.response:<15.15}"
        )


def init(stdout_lock: multiprocessing.Lock) -> None:
    """
    Initialize the global multiprocessing lock for output to stdout.
    """
    global lock
    lock = stdout_lock

    global dns_records
    dns_records = {}

    global locations
    locations = {}

    global asns
    asns = {}


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Perform a traceroute against a given target(s).")

    # either allow an input file, or a target address. not both
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument("-c", "--csv", type=str, help="Input CSV file.")
    target_group.add_argument("-t", "--target", type=str, help="Target destination.")

    parser.add_argument(
        "-P",
        "--protocol",
        default="all",
        type=str,
        choices=["udp", "tcp", "icmp", "http", "tls"],
        help="protocol choice (default: %(default)s)",
    )
    parser.add_argument(
        "-m",
        "--max_ttl",
        default=30,
        type=int,
        help="Set the max time-to-live (max number of hops) used in outgoing probe packets.",
    )
    parser.add_argument(
        "-T",
        "--timeout",
        default=5,
        type=int,
        help="Set the time (in seconds) to wait for a response to a probe (default 5 sec.).",
    )
    parser.add_argument(
        "--threads",
        default=4,
        type=int,
        help="Maximum number of concurrent traceroutes.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose logging.",
    )
    parser.add_argument(
        "-s",
        "--stealth",
        action="store_true",
        default=False,
        help="Sleep for random periods in between requests to avoid ISP detection.",
    )
    args = parser.parse_args()

    # set log level to debug if verbose flag is passed
    if args.verbose:
        coloredlogs.install(
            level="DEBUG", fmt="%(asctime)s - %(levelname)s - %(message)s"
        )

    targets = []

    if args.csv:
        targets = read_csv_input_file(args.csv)
        if not targets:
            sys.exit(1)

    elif args.target:
        targets.append(args.target)

    else:
        log.error("You must provide either a target or an input file. Exiting...")
        parser.print_help()
        sys.exit(1)

    # if we are in stealth mode, then we will only want to request one resource
    # at a time
    if args.stealth:
        thread_count = 1

    else:
        # only spawn multiple threads if we have multiple targets
        thread_count = len(targets) if len(targets) < args.threads else args.threads

    # default run all protocols
    if args.protocol == "all":
        protocols = ["icmp", "tcp", "udp", "http", "tls"]
    else:
        protocols = [args.protocol]

    start_time = time.time()

    for protocol in protocols:

        # initialize a thread pool for each target in the list with
        # a lock for the multiprocessing pool for output to stdout
        with multiprocessing.Pool(
            processes=thread_count, initializer=init, initargs=(multiprocessing.Lock(),)
        ) as pool:

            log.info(f"Initializing traceroute via {protocol}...")

            # zip up the arguments as all of the targets, repeating the protocol,
            # max_ttl, and timeout for each individual traceroute
            try:
                pool.starmap(
                    Traceroute,
                    zip(
                        targets,
                        repeat(protocol),
                        repeat(args.max_ttl),
                        repeat(args.timeout),
                        repeat(args.stealth),
                    ),
                )
            except KeyboardInterrupt:
                log.warning("\nKeyboard interrupt received, exiting...")
                pool.close()

    log.info(f"\nTotal elapsed time: {time.time() - start_time:.2f} seconds.")
