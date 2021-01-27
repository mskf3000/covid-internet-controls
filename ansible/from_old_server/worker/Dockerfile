FROM python:latest

HEALTHCHECK --interval=5m --timeout=3s \
    CMD curl -f http://localhost:42075/ping || exit 1

COPY ./ /src

RUN pip install --no-cache-dir -r /src/requirements.txt

EXPOSE 42075

ENTRYPOINT ["gunicorn", "--chdir", "/src", "run_worker:app", "-w", "2", "--threads", "2", "-b", "0.0.0.0:42075"]