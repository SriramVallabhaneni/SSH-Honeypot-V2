from typing import Any


class HoneypotRepository:
    def __init__(self, connection):
        self.connection = connection

    def insert_connection(self, record: dict[str, Any]) -> int:
        query = """
        INSERT INTO connections (
            timestamp,
            source_ip,
            source_port,
            client_banner,
            country,
            city,
            latitude,
            longitude,
            auth_attempt_count,
            duration_seconds
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """

        values = (
            record["timestamp"],
            record["source_ip"],
            record["source_port"],
            record.get("client_banner"),
            record.get("country"),
            record.get("city"),
            record.get("latitude"),
            record.get("longitude"),
            record["auth_attempt_count"],
            record["duration_seconds"],
        )

        with self.connection.cursor() as cur:
            cur.execute(query, values)
            connection_id = cur.fetchone()["id"]
        self.connection.commit()
        return connection_id

    def insert_credentials(self, connection_id: int, credentials: list[dict[str, str]]) -> None:
        if not credentials:
            return

        query = """
        INSERT INTO credentials (connection_id, username, password)
        VALUES (%s, %s, %s);
        """

        rows = [
            (connection_id, item["username"], item["password"])
            for item in credentials
        ]

        with self.connection.cursor() as cur:
            cur.executemany(query, rows)
        self.connection.commit()

    def get_total_attempts(self) -> int:
        query = "SELECT COUNT(*) AS count FROM connections;"
        with self.connection.cursor() as cur:
            cur.execute(query)
            return cur.fetchone()["count"]


    def get_unique_ips(self) -> int:
        query = "SELECT COUNT(DISTINCT source_ip) AS count FROM connections;"
        with self.connection.cursor() as cur:
            cur.execute(query)
            return cur.fetchone()["count"]


    def get_total_credentials(self) -> int:
        query = "SELECT COUNT(*) AS count FROM credentials;"
        with self.connection.cursor() as cur:
            cur.execute(query)
            return cur.fetchone()["count"]  