import os
import socket
import threading

import paramiko

from app.db.init_db import get_db_connection
from app.db.repository import HoneypotRepository
from app.enrichment.geoip import enrich_ip
from app.honeypot.auth import SSHServerHandler
from app.honeypot.config import Config
from app.honeypot.session import SessionRecord


HOST_KEY_PATH = "server.key"


def load_or_create_host_key(path: str = HOST_KEY_PATH) -> paramiko.RSAKey:
    if os.path.exists(path):
        return paramiko.RSAKey(filename=path)

    key = paramiko.RSAKey.generate(2048)
    key.write_private_key_file(path)
    return key


def handle_connection(client_socket, client_address, host_key, config: Config) -> None:
    session = SessionRecord(
        source_ip=client_address[0],
        source_port=client_address[1],
    )

    transport = None
    try:
        transport = paramiko.Transport(client_socket)
        transport.local_version = config.ssh_banner
        transport.add_server_key(host_key)

        handler = SSHServerHandler(session)
        transport.start_server(server=handler)

        session.client_banner = transport.remote_version
        transport.accept(5)

    except Exception:
        pass
    finally:
        session.finish()

        geo = enrich_ip(session.source_ip, config)
        if geo:
            session.country = geo.get("country")
            session.city = geo.get("city")
            session.latitude = geo.get("latitude")
            session.longitude = geo.get("longitude")

        with get_db_connection(config) as connection:
            repo = HoneypotRepository(connection)
            connection_id = repo.insert_connection(session.to_connection_dict())
            repo.insert_credentials(connection_id, session.to_credentials_list())

        if transport:
            transport.close()
        client_socket.close()


def start_server(config: Config) -> None:
    host_key = load_or_create_host_key()
    semaphore = threading.Semaphore(config.max_connections)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((config.honeypot_host, config.honeypot_port))
    server_socket.listen(100)

    try:
        while True:
            client_socket, client_address = server_socket.accept()

            def wrapped_handler():
                with semaphore:
                    handle_connection(client_socket, client_address, host_key, config)

            thread = threading.Thread(target=wrapped_handler, daemon=True)
            thread.start()
    finally:
        server_socket.close()