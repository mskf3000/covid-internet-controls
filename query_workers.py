#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys
from itertools import repeat
from multiprocessing.pool import Pool

import coloredlogs
import mysql.connector
import requests
from dotenv import load_dotenv
from workers import workers
from datetime import datetime
import time
from random import randrange


load_dotenv()
log = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="%(message)s")

REQUEST_KEY = os.getenv("REQUEST_KEY")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"


def ping(worker: str):
    """ Ping a worker for connectivity. """

    log.debug(f"Pinging {worker}...")

    pingable = False

    try:
        response = requests.get(f"http://{worker}:42075/ping", timeout=15)

    except requests.ConnectionError as e:
        log.debug(f"Connecting to {worker} yielded: {e}")

    else:

        data = response.json()

        try:
            if data["status"] == "success":
                pingable = True

        except KeyError:
            log.error("Invalid response.")

    finally:
        return pingable


def send_target_to_worker(worker: dict, target: str):
    """ Send a target to a single worker. """	
    time.sleep(randrange(20)+1)
    data = {"key": REQUEST_KEY, "target": target}
    log.debug(f"Sending {target} to {worker['country_name']}...")
    address = f"http://{worker['ip']}:42075/new_target"

    try:
        response = requests.post(address, data=data, timeout=25).json()

    except requests.RequestException as e:
        response = {"target": target, "success": False, "data": str(e)}

    log.debug(f"{json.dumps(response, indent=4)}")
    response["worker"] = worker
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    response["date"] = formatted_date
    return response


def strip_protocol(url: str):
    url = url.replace("http://", "")
    url = url.replace("https://", "")
    return url


def get_domain_name_from_url(url: str):
    """
    Parse a URL and extract the domain name without any extras (port, etc.)
    """

    # strip protocol
    url = strip_protocol(url)

    # now strip path
    url = url.split("/")
    url = url[0]

    # strip port, if existing
    url = url.split(":")[0]

    if not url.startswith("www."):
        url = "www." + url

    return url


def get_path_from_url(url: str):
    url = strip_protocol(url)

    url_split = url.split("/")
    path = "/"
    if len(url_split) > 1:
        path = path + "/".join(url_split[1:])

    return path


def setup_db():
    conn = mysql.connector.connect(
#        host=MYSQL_HOST,
#        user=MYSQL_USER,
#        passwd=MYSQL_PASSWORD,
#        database="covid_internet_controls",
        host="127.0.0.1",
        user= "sahilgupta221",
        passwd="easypass321!",
        database="covid_internet_controls",

    )
    if conn.is_connected():
        return conn

    log.error("Unable to establish a connection to the database.")
    return None


def send_to_db(conn, sql, values):
    log.debug(f"sql is {sql}")
    log.debug(f"values are {values}")
    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()


def get_from_db(conn, sql, values):
    log.debug(f"sql is {sql}")
    log.debug(f"values are {values}")
    cursor = conn.cursor()
    cursor.execute(sql, values)
    results = cursor.fetchall()
    return results


def send_worker_to_db(conn, worker):
    log.info(f"Updating DB for worker {worker['ip']}...")
    sql = "INSERT IGNORE INTO countries VALUES (%s, %s, %s)"
    values = (worker["country_code"], worker["country_name"], worker["continent"])
    send_to_db(conn, sql, values)

    sql = "INSERT IGNORE INTO workers VALUES (%s, %s, %s)"
    values = (worker["ip"], worker["country_code"], worker["city"])
    send_to_db(conn, sql, values)


def get_response_id(conn, content):
    sql = "SELECT id FROM response WHERE content_hash = MD5(%s)"
    values = (content,)
    response = get_from_db(conn, sql, values)
    if len(response) > 0:
        return response[0][0]
    return None


def send_results_to_db(conn, worker, results):
    log.info(f"Sending results for {worker['ip']} ({worker['country_name']})...")
    domain = get_domain_name_from_url(results["target"])
    path = get_path_from_url(results["target"])

    if "http://" in results["target"]:
        protocol = "http"
    else:
        protocol = "https"

    if results["success"] is False:
        sql = "INSERT INTO request (worker_ip, domain, path, protocol, censored) VALUES (%s, %s, %s, %s, %s)"
        values = (worker["ip"], domain, path, protocol, True)
        send_to_db(conn, sql, values)

    else:
        response_id = get_response_id(conn, results["content"])

        if not response_id:
            log.debug("Response does not currently exist, entering it now...")
            sql = "INSERT INTO response (success, status_code, content, content_hash) VALUES (%s, %s, %s, MD5(%s))"
            values = (
                results["success"],
                results["status_code"],
                results["content"],
                results["content"],
            )
            send_to_db(conn, sql, values)

        response_id = get_response_id(conn, results["content"])

        sql = "INSERT INTO request (worker_ip, domain, path, response_id, protocol, censored,date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (worker["ip"], domain, path, response_id, protocol, False, results["date"])
        send_to_db(conn, sql, values)

    # sql = "INSERT INTO request VALUES (%s, %s, %s, %s, %s)"


def send_target_to_workers(target: str, workers: list):
    """ Send a target to all workers in a multiprocessing pool. """

    with Pool(processes=60) as pool:
        results = list(
            pool.starmap(send_target_to_worker, zip(workers, repeat(target)))
        )

	
        # put all results into respective lists so that we can print successes
        # first, then the failures
        successes = []
        failures = []

        for result in results:
            status_line = f"{BOLD}{result['worker']['country_name']:<20}{RESET}"

            if result["success"]:
                successes.append(
                    status_line + f"{GREEN}SUCCESS - {result['status_code']}{RESET}"
                )

            else:

                # if we did not have success, verify that the worker
                # is not just offline
                if not ping(result["worker"]["ip"]):
                    status_line += f"{RED}ERROR - Worker is offline{RESET}"

                else:
                    status_line += f"{RED}ERROR - {result['data']}{RESET}"

                failures.append(status_line)

        for success in successes:
            print(success)

        for failure in failures:
            print(failure)

        return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose logging.",
    )
    parser.add_argument(
        "-t",
        "--target",
        type=str,
        help="Send a target to a given worker (defaults to all workers).",
    )
    parser.add_argument(
        "-w", "--worker", type=str, help="Send targets to a specific worker."
    )

    args = parser.parse_args()

    # set log level to debug if verbose flag is passed
    if args.verbose:
        coloredlogs.install(
            level="DEBUG", fmt="%(asctime)s - %(levelname)s - %(message)s"
        )

    if args.target:

        # if sending targets, see if we are targeting a specific worker.
        # if so, we need to parse the workers file for the corresponding
        # server location to get its IP address
        if args.worker:

            target_worker = None
            for worker in workers:
                if worker["country_name"].lower() == args.worker.lower():
                    target_worker = worker

            if not target_worker:
                log.error(f"Worker '{args.worker}' does not exist.")
                sys.exit(1)

            workers = [target_worker]

        # otherwise, default to sending target to all workers
        else:
            workers = workers

        log.info(f"Requesting {args.target}...")
        results = send_target_to_workers(args.target, workers)
        conn = setup_db()
        if not conn:
            sys.exit(1)

        for worker in workers:
            send_worker_to_db(conn, worker)

        for result in results:
            if ping(result["worker"]["ip"]):
                send_results_to_db(conn, result["worker"], result)

    # if we are not sending targets, then just ping all workers
    else:

        for worker in workers:
            if ping(worker["ip"]):
                print(f"{worker['country_name']:<20} OK")
            else:
                print(f"{worker['country_name']:<20} OFFLINE")



