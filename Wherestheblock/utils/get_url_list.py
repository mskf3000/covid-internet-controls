#!/usr/bin/env python3
import argparse
import logging
import os
from pathlib import Path

import coloredlogs
import requests

log = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="%(message)s")

INPUT_DIRECTORY = os.path.join(Path(__file__).resolve().parents[1], "input")

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Download URL lists from CitizenLab.")
    parser.add_argument(
        "-c",
        "--country",
        type=str,
        required=True,
        help="Country code for the desired URL list.",
    )
    args = parser.parse_args()
    country_code = args.country.lower()

    target_url = f"https://raw.githubusercontent.com/citizenlab/test-lists/master/lists/{country_code}.csv"
    log.debug(f"Target URL is {target_url}...")

    response = requests.get(target_url)

    if response.status_code != 200:
        log.error(f"No URL list exists for {country_code}.")

    else:
        log.debug(f"Received the following results: \n{response.text}")
        file_path = os.path.join(INPUT_DIRECTORY, f"{country_code}.csv")

        log.debug(f"Writing results to {file_path}...")
        with open(file_path, "w") as url_list:
            url_list.write(response.text)

        log.info(f"URL list downloaded for '{country_code}' to {file_path}.")
