from psycopg import connect
from psycopg.rows import dict_row

from app.honeypot.config import Config


def get_db_connection(config: Config):
    return connect(
        dbname=config.postgres_db,
        user=config.postgres_user,
        password=config.postgres_password,
        host=config.postgres_host,
        port=config.postgres_port,
        row_factory=dict_row,
    )


def initialize_db(config: Config) -> None:
    create_connections_table = """
    CREATE TABLE IF NOT EXISTS connections (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMPTZ NOT NULL,
        source_ip INET NOT NULL,
        source_port INTEGER NOT NULL,
        client_banner TEXT,
        country TEXT,
        city TEXT,
        latitude DOUBLE PRECISION,
        longitude DOUBLE PRECISION,
        auth_attempt_count INTEGER NOT NULL DEFAULT 0,
        duration_seconds DOUBLE PRECISION NOT NULL DEFAULT 0
    );
    """

    create_credentials_table = """
    CREATE TABLE IF NOT EXISTS credentials (
        id SERIAL PRIMARY KEY,
        connection_id INTEGER NOT NULL REFERENCES connections(id) ON DELETE CASCADE,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    );
    """

    with get_db_connection(config) as conn:
        with conn.cursor() as cur:
            cur.execute(create_connections_table)
            cur.execute(create_credentials_table)
        conn.commit()