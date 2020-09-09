#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import coloredlogs
import mysql.connector
from dotenv import load_dotenv
#from datetime import datetime
import pathlib
from pathlib import Path
import time

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

"""

def send_results_to_db(conn, worker, resimport time

print("Printed immediately.")
time.sleep(2.4)ults):
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
"""

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

    conn = setup_db()
    if not conn:
        sys.exit(1)
    else:
        print(conn)
    os.system("rm -r 20*")
    time.sleep(7)
    cursor = conn.cursor()
    sql = "select * from request as req JOIN response as res ON req.response_id = res.id JOIN workers as w ON req.worker_ip = w.worker_ip"
    values = ()
    cursor.execute(sql, values)
    results = cursor.fetchall()
    for res in results:
        print(str(res[7]).replace(" ","_")+"_"+res[13]+"_"+res[14],res[2],res[3])
        Path(str(res[7]).replace(" ","_").partition("_")[0]+"/"+res[13]+"_"+res[14]).mkdir(parents=True, exist_ok=True)
        os.system("touch "+str(res[7]).replace(" ","_").partition("_")[0]+"/"+res[13]+"_"+res[14]+"/"+str(res[2]+res[3]).replace("/","")+".html")
        f = open(str(res[7]).replace(" ","_").partition("_")[0]+"/"+res[13]+"_"+res[14]+"/"+str(res[2]+res[3]).replace("/","")+".html", 'wb')
        message = res[11]
        f.write(message)
        f.close()


# content: res[11]
#    print(pathlib.Path(__file__).parent.absolute())
#    print(pathlib.Path().absolute())
    # if not os.path.exists("directory"):
    #     os.makedirs("directory")
    #print(results[0][15], results[0][14], results[0][13])
    # city name : results[0][15]
    # send_worker_to_db(conn, worker)
    # send_results_to_db(conn, result["worker"], result)
