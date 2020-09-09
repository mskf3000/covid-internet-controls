import pytest
import os
from dotenv import load_dotenv
from worker.run_worker import app, request_webpage

load_dotenv()


@pytest.fixture
def worker():
    app.config["TESTING"] = True

    with app.test_client() as worker:
        yield worker


def test_get_request(worker):
    """Test get request instead of post."""

    req = worker.get("/new_target")
    assert req.status_code == 405


# def test_invalid_key(worker):
#    """Test failure without the correct authentication key."""
#    data = {"key": "invalid"}
#    req = worker.post("/new_target", data=data)
#    assert req.get_json()["status"] == "error"
#    assert req.get_json()["data"] == "Invalid key."


def test_invalid_request(worker):
    """Test a request with valid key but invalid 'target' key.."""

    data = {"invalid": "format", "key": os.getenv("REQUEST_KEY")}
    req = worker.post("/new_target", data=data)
    assert req.get_json()["status"] == "error"
    assert req.get_json()["data"] == "Invalid data format. Need target."


def test_empty_request(worker):
    """Test an empty post request."""

    req = worker.post("/new_target")
    assert req.get_json()["status"] == "error"


def test_ping(worker):
    """Test a ping check."""

    req = worker.get("/ping")
    assert req.get_json()["status"] == "success"
    assert req.get_json()["data"] == "pong"


def test_new_target_http_redirect(worker):
    """Test a new target, getting a 301 to the HTTPS version."""

    data = {"target": "google.com", "key": os.getenv("REQUEST_KEY")}
    req = worker.post("/new_target", data=data)
    assert req.get_json()["status_code"] == 301


def test_new_target(worker):
    """Test a new target."""

    data = {"target": "https://www.google.com", "key": os.getenv("REQUEST_KEY")}
    req = worker.post("/new_target", data=data)
    assert req.get_json()["status_code"] == 200


def test_request_webpage_redirect():
    """ Test that we get a redirect for non-https. """

    website = "www.wikipedia.org"
    assert request_webpage(website)["status_code"] == 301


def test_request_webpage_success():
    """ Test that an HTTPS request works. """

    website = "https://www.wikipedia.org"
    assert request_webpage(website)["status_code"] == 200


def test_request_webpage_failure():
    """ Test that a non-existent website fails. """

    website = "aaaaaaaa"
    assert request_webpage(website, timeout=1)["success"] is False
