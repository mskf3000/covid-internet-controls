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


def traceroute_of_type(requested_target: str,requested_type: str):
    #run wtb script
    #import wtb 
    
    #not familier with the workflow of this python script, so just going to focus on running it right now and making sure this works
    import sys
    script_descriptor = open("wtb.py")
    a_script = script_descriptor.read()
    sys.argv = ["wtb.py","-t","129.21.14.15","-P","udp"]
    exec(a_script)
    script_descriptor.close()
    #end temp code
    
    #build output, needs to come from method resc
    data = {
        "requested_type": requested_type,
        "target": requested_target,
        "success": True,
    }
    
    return data#return the json created by the previous script's methods

@app.route("/tracert", methods=["POST"])
def tracert():
    """ Respond to a new target request. """
    #testing without input
    try:
        requested_target = request.form["target"]
        requested_type = request.form["type"]
    
    except KeyError:
        return make_response("error", "Invalid data format. Need target & type.")
    #requested_target = "";requested_type = "";
    #return traceroute_of_type(requested_target,requested_type)
    #traceroute_of_type(requested_target,requested_type)
    
    script_descriptor = open("wtb.py")
    a_script = script_descriptor.read()
    sys.argv = ["wtb.py","-t","129.21.14.15","-P","udp"]
    exec(a_script)
    script_descriptor.close() 
    
    return "<h1>namita's test string</h1>"
    #return jsonify(request.args)
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=42075)
