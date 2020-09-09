#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import coloredlogs
import mysql.connector
from dotenv import load_dotenv
import pathlib
from pathlib import Path
import time
import json
load_dotenv()
log = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="%(message)s")

def setup_db():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user= "sahilgupta221",
        passwd="easypass321!",
        database="covid_internet_controls",
    )
    if conn.is_connected():
        return conn

    log.error("Unable to establish a connection to the database.")
    return None

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
    time.sleep(3)
    cursor = conn.cursor()
    sql = "select * from request as req JOIN response as res ON req.response_id = res.id JOIN workers as w ON req.worker_ip = w.worker_ip"
    values = ()
    cursor.execute(sql, values)
    results = cursor.fetchall()
    for res in results:
        print(str(res[7]).replace(" ","_")+"_"+res[13]+"_"+res[14],res[2],res[3])
        Path(str(res[7]).replace(" ", "_").partition("_")[0] + "/" + str(res[2]+res[3]).replace("/","")).mkdir(parents=True,
                                                                                        exist_ok=True)
        os.system(
            "touch " + str(res[7]).replace(" ", "_").partition("_")[0] + "/" + str(res[2]+res[3]).replace("/","") + "/" + res[13]+"_"+res[14] + ".html")
        f = open(str(res[7]).replace(" ", "_").partition("_")[0] + "/" + str(res[2]+res[3]).replace("/","") + "/" + res[13]+"_"+res[14] + ".html", 'wb')
        message = res[11]
        f.write(message)
        f.close()

