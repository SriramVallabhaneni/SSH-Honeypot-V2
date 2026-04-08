import time

from prometheus_client import start_http_server

from app.db.init_db import get_db_connection
from app.db.repository import HoneypotRepository
from app.exporter.metrics import update_metrics
from app.honeypot.config import Config


def start_exporter(config: Config) -> None:
    start_http_server(config.exporter_port)

    while True:
        with get_db_connection(config) as connection:
            repo = HoneypotRepository(connection)
            update_metrics(repo)

        time.sleep(config.metrics_refresh_seconds)