#!/usr/bin/env python3

import logging
import os

import requests
from dotenv import load_dotenv
from fake_useragent import UserAgent
from flask import Flask, jsonify, request

app = Flask(__name__)
log = logging.getLogger(__name__)
logging.getLogger("scapy").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.WARNING)
load_dotenv()

REQUEST_KEY = os.getenv("REQUEST_KEY")


# def verify_request(key: str):
#    """Verify a given request, ensuring the request key matches."""

#    if key != REQUEST_KEY:
#        return False
#    return True


def request_webpage(target: str, timeout: int = 10):
    """ Request a given webpage, returning the received response. """

    if not target.startswith("http://") and not target.startswith("https://"):
        target = f"http://{target}"

    headers = {"User-Agent": UserAgent().random}
    data = {"success": False}

    try:
        response = requests.get(
            target, headers=headers, timeout=timeout, allow_redirects=False
        )

    except requests.RequestException as e:
        error_message = f"Request exception for {target}: {str(e)}"
        log.error(error_message)
        data["data"] = error_message

    else:

        try:
            content = response.content.decode(response.encoding or "utf-8")

        except UnicodeDecodeError:
            content = response.text

        data = {
            "target": target,
            "headers": dict(response.headers),
            "status_code": response.status_code,
            "success": True,
            "content": content,
        }

    finally:
        return data


def make_response(status: str, data: str = ""):
    """ Make a simple response. """
    return jsonify({"status": status, "data": data})


@app.route("/ping", methods=["GET"])
def ping():
    """ Respond to a given ping request. """
    return make_response("success", "pong")


@app.route("/new_target", methods=["POST"])
def new_target():
    """ Respond to a new target request. """
    #    try:
    #        if not verify_request(request.form["key"]):
    #            return make_response("error", "Invalid key.")

    #    except KeyError:
    #        return make_response("error", "Key parameter required.")

    try:
        requested_target = request.form["target"]

    except KeyError:
        return make_response("error", "Invalid data format. Need target.")

    return request_webpage(requested_target)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=42075)
