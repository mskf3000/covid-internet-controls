#!/usr/bin/env python3

import argparse
import csv
import logging
import os
from pathlib import Path

import coloredlogs
import requests

log = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="%(message)s")


def get_url_list(country_code: str):
    """
    Get the raw results for a specific citizenlab country code listing.
    """

    target_url = f"https://raw.githubusercontent.com/citizenlab/test-lists/master/lists/{country_code}.csv"
    log.debug(f"Target URL is {target_url}...")

    response = requests.get(target_url)

    content = ""
    if response.status_code != 200:
        log.error(f"No URL list exists for {country_code}.")

    else:
        content = response.text
        log.debug(f"Received the following results: \n{response.text}")

    return content


def format_csv_results(response: str):
    """
    Format the raw CSV results received from the Github page.
    """

    targets = []
    try:
        csv_reader = csv.DictReader(response.splitlines())

    except OSError:
        log.error(f"Unable to parse response CSV.")

    else:

        # some of the url lists have the key as URL, others have it as url.
        # ¯\_(ツ)_/¯
        if "url" in csv_reader.fieldnames:
            key_value = "url"

        elif "URL" in csv_reader.fieldnames:
            key_value = "URL"

        else:
            log.error(f"Invalid CSV format: unable to grab URL key.")
            return

        targets = [row[key_value] for row in csv_reader]

    finally:
        log.debug(f"Final results: \n{targets}")
        return targets


def save_url_list_to_file(url_list: str, country_code: str):
    """
    Save the URL list to the input directory.
    """

    INPUT_DIRECTORY = os.path.join(Path(__file__).resolve().parents[1], "input")
    file_path = os.path.join(INPUT_DIRECTORY, f"{country_code}.txt")

    log.debug(f"Writing results to {file_path}...")
    try:
        with open(file_path, "w") as url_file:
            for url in url_list:
                url_file.write(f"{url}\n")

        log.info(f"URL list downloaded for '{country_code}' to {file_path}.")

    except OSError as e:
        log.error(f"Unable to save URL list: {e}")


def main(country_code):
    url_list = get_url_list(country_code)
    if not url_list:
        exit()

    formatted_results = format_csv_results(url_list)
    if not formatted_results:
        exit()

    save_url_list_to_file(formatted_results, country_code)


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

    main(country_code)
