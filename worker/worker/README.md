# Worker

Each VPS that is used for gathering data is classified as a `worker`. The architecture for this is as follows:

1. Ansible is used to designate and configure a new VPS.
2. A Python Docker container is created to run using `run_worker.py`.
3. [gunicorn](https://gunicorn.org) is used to act as a WSGI HTTP server for interfacing requests to Flask. 
4. Flask is run with endpoints for pinging a given worker and listening for new requests.

All requests need to pass a valid `REQUEST_KEY` in order to get a valid response.