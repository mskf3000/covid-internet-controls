#!/usr/bin/env python3

import json
import os
import re
from datetime import datetime
from prettytable import PrettyTable
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from src.worker.utils.redis_utils import RedisConnection

load_dotenv()
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")


def calculate_sucess(hops: list) -> int:
    """ calculate number of hops until traceroute success """
    for ct, hop in enumerate(hops):
        if hop["success"]:
            return ct + 1
    return len(hops)


def calculate_date(date: str) -> datetime:
    """ convert date timestamp string to datetime object """
    return datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")


def write_output_to_file(output: list) -> None:
    """ write the list of data to an output file """
    with open("hop_counts.txt", "w") as out_file:
        for line in output:
            out_file.write(line + "\n")


def remove_script(text):
    return "".join([word for i, word in enumerate(text.split("script")) if i % 2 == 0])


def remove_style(text):
    out = []
    for i, word in enumerate(text.split("style")):
        if i % 2 == 0:
            out.append(word)
    return "".join(out)


def find_censorship():
    redis = RedisConnection(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)

    if not redis.connection:
        exit()

    keys = redis.get_keys()
    out = []

    servers = {
        "95.141.43.68": "Italy",
        "46.4.164.170": "Germany",
        "102.67.140.37": "South Africa",
        "54.37.138.54": "Poland",
        "109.201.143.179": "Australia",
        "150.95.190.42": "Japan",
        "103.140.45.134": "Korea",
        "51.79.129.161": "Malaysia",
        "111.231.28.232": "Shanghai",
        "185.123.101.36": "Turkey",
        "45.136.56.45": "Kazakhstan",
        "45.7.230.136": "Peru",
        "138.118.174.43": "Brazil",
        "94.156.174.142": "Bulgaria",
        "41.223.52.107": "Egypt",
        "103.205.9.38": "Hong Kong",
    }

    # disregard tcp
    DESIRED_PROTOCOLS = ["https", "http", "icmp", "udp"]
    BLOCKED_KEYWORDS = ["blocked", "censored"]
    TARGET_STATUS_CODES = [451, 410, 308, 403, 415]
    STATUS_CODES = {}

    censorship_results = []
    # go through each target
    # for key in keys:

    # now go through each trace to each target
    records = redis.get("www.douban.com")
    sources = {}

    # filter by IP address
    for traceroute in records:
        ip = traceroute["global_ip"]
        if ip not in sources.keys():
            sources[ip] = [traceroute]
        else:
            sources[ip].append(traceroute)

    x = PrettyTable()
    b = "\033[1m"
    r = "\033[0m"
    x.field_names = [
        f"{b}IP ADDRESS{r}",
        f"{b}COUNTRY{r}",
        f"{b}HTTPS{r}",
        f"{b}HTTP{r}",
        f"{b}ICMP{r}",
        f"{b}TCP{r}",
    ]

    # go through each source VPS and the traceroutes
    for ip, traceroutes in sources.items():

        COUNTS = {}

        # calculate number of protocol traces and total hops per protocol
        for traceroute in traceroutes:
            success = calculate_sucess(traceroute["hops"])

            if traceroute["protocol"] not in COUNTS.keys():
                COUNTS[traceroute["protocol"]] = {"total": 1, "count": success}

            else:
                COUNTS[traceroute["protocol"]["total"]] += 1
                COUNTS[traceroute["protocol"]] += success

        ip_s = ip.split(".")
        ip_s = ip_s[0] + ".xXx.XxX.xXx"
        l = [ip_s, servers[ip]]
        for protocol in ["https", "http", "icmp", "tcp"]:
            l.append(COUNTS[protocol]["count"] / COUNTS[protocol]["total"])

        x.add_row(l)

    x.align["IP ADDRESS"] = "l"
    print("\n\n\n\033[1;32mAverage Hop Counts to Douban.com\033[0m")
    print(x)
    # if traceroute["protocol"] == "http" or traceroute["protocol"] == "https":
    #    for hop in traceroute["hops"]:
    #        if "http_content" in hop.keys():

    # if hop["http_content"]["status_code"] != 200:

    # traceroute["results"] = hop["http_content"]
    # del traceroute["hops"]
    # censorship_results.append(traceroute)
    # break

    with open("results.json", "w") as json_file:
        json.dump(censorship_results, json_file, indent=4)


if __name__ == "__main__":
    find_censorship()
