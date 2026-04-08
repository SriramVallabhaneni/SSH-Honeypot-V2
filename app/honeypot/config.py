import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Config:
    app_env: str
    log_level: str
    honeypot_host: str
    honeypot_port: int
    max_connections: int
    ssh_banner: str
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    exporter_port: int
    metrics_refresh_seconds: int
    geoip_api_url: str
    geoip_timeout_seconds: int
    geoip_cache_ttl_seconds: int


def _get_required(key: str) -> str:
    value = os.getenv(key)
    if value is None or value.strip() == "":
        raise ValueError(f"Missing required environment variable: {key}")
    return value


def load_config() -> Config:
    return Config(
        app_env=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        honeypot_host=os.getenv("HONEYPOT_HOST", "0.0.0.0"),
        honeypot_port=int(os.getenv("HONEYPOT_PORT", "2222")),
        max_connections=int(os.getenv("MAX_CONNECTIONS", "50")),
        ssh_banner=os.getenv(
            "SSH_BANNER",
            "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5",
        ),
        postgres_db=_get_required("POSTGRES_DB"),
        postgres_user=_get_required("POSTGRES_USER"),
        postgres_password=_get_required("POSTGRES_PASSWORD"),
        postgres_host=_get_required("POSTGRES_HOST"),
        postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
        exporter_port=int(os.getenv("EXPORTER_PORT", "8000")),
        metrics_refresh_seconds=int(os.getenv("METRICS_REFRESH_SECONDS", "15")),
        geoip_api_url=os.getenv("GEOIP_API_URL", "http://ip-api.com/json"),
        geoip_timeout_seconds=int(os.getenv("GEOIP_TIMEOUT_SECONDS", "3")),
        geoip_cache_ttl_seconds=int(os.getenv("GEOIP_CACHE_TTL_SECONDS", "86400")),
    )