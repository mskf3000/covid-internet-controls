#!/usr/bin/env python3

"""
Grab the latest GeoLite databases from Maxmind.
"""

import logging
import os
import shutil
import tarfile

import coloredlogs
import requests

from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="%(message)s")

BASE_URL = "https://download.maxmind.com/app/geoip_download"
DATABASE_LOCATION = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "geolite_databases"
)
WORKDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")

LICENSE_KEY = os.getenv("MAXMIND_LICENSE_KEY")
if not LICENSE_KEY:
    log.error(
        "No license key is set. You must create a .env file defining it as MAXMIND_LICENSE_KEY=''. Exiting..."
    )
    exit(1)

database_types = ["ASN", "City"]
os.makedirs(WORKDIR, exist_ok=True)

for database in database_types:
    params = {
        "edition_id": f"GeoLite2-{database}",
        "license_key": "QMgqUyaCCex4fuFc",
        "suffix": "tar.gz",
    }

    log.info(f"Downloading {database} from maxmind...")
    response = requests.get(BASE_URL, params=params, stream=True)

    if response.status_code == 200:

        tgz_filepath = os.path.join(WORKDIR, f"GeoLite2-{database}.tar.gz")
        log.debug(f"{database} database received, saving to {tgz_filepath}...")

        with open(tgz_filepath, "wb") as f:
            f.write(response.content)

        log.debug(f"Save completed, extracting contents to {WORKDIR}...")

        with tarfile.open(tgz_filepath) as tar:

            # extract the name of the database from the tarfile
            members = tar.getmembers()
            file_name = ""
            for member in members:
                if "mmdb" in member.name:
                    file_name = member.name

            if not file_name:
                log.error("No database file retrieved.")
                exit()

            log.debug(f"Database file is {file_name}, extracting...")
            tar.extract(file_name, path=WORKDIR)

        # shutil wont move the file if it exists, so remove the old one first
        if os.path.exists(os.path.join(DATABASE_LOCATION, os.path.basename(file_name))):
            log.debug(f"Removing old database file...")
            os.remove(os.path.join(DATABASE_LOCATION, os.path.basename(file_name)))

        file_path = os.path.join(WORKDIR, file_name)
        log.debug(f"Moving database file to {DATABASE_LOCATION}...")

        shutil.move(file_path, DATABASE_LOCATION)

        log.info(f"{database} database download complete.")
    else:
        log.error(
            f"Received {response.status_code} status code requesting database {database}."
        )
