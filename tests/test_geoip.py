from app.enrichment.geoip import enrich_ip
from app.honeypot.config import Config


def build_config() -> Config:
    return Config(
        app_env="test",
        log_level="INFO",
        honeypot_host="0.0.0.0",
        honeypot_port=2222,
        max_connections=50,
        ssh_banner="SSH-2.0-test",
        postgres_db="honeypot",
        postgres_user="honeypot",
        postgres_password="honeypot",
        postgres_host="localhost",
        postgres_port=5432,
        exporter_port=8000,
        metrics_refresh_seconds=15,
        geoip_api_url="http://ip-api.com/json",
        geoip_timeout_seconds=3,
        geoip_cache_ttl_seconds=86400,
    )


def test_enrich_ip_returns_none_for_loopback_ip() -> None:
    config = build_config()

    result = enrich_ip("127.0.0.1", config)

    assert result is None


def test_enrich_ip_returns_none_for_private_ip() -> None:
    config = build_config()

    result = enrich_ip("192.168.1.10", config)

    assert result is None