from app.honeypot.config import load_config


def test_load_config_reads_environment(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("HONEYPOT_HOST", "127.0.0.1")
    monkeypatch.setenv("HONEYPOT_PORT", "2222")
    monkeypatch.setenv("MAX_CONNECTIONS", "25")
    monkeypatch.setenv("SSH_BANNER", "SSH-2.0-test")
    monkeypatch.setenv("POSTGRES_DB", "honeypot")
    monkeypatch.setenv("POSTGRES_USER", "honeypot")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("EXPORTER_PORT", "8000")
    monkeypatch.setenv("METRICS_REFRESH_SECONDS", "15")
    monkeypatch.setenv("GEOIP_API_URL", "http://ip-api.com/json")
    monkeypatch.setenv("GEOIP_TIMEOUT_SECONDS", "3")
    monkeypatch.setenv("GEOIP_CACHE_TTL_SECONDS", "86400")

    config = load_config()

    assert config.app_env == "test"
    assert config.log_level == "DEBUG"
    assert config.honeypot_host == "127.0.0.1"
    assert config.honeypot_port == 2222
    assert config.max_connections == 25
    assert config.ssh_banner == "SSH-2.0-test"
    assert config.postgres_db == "honeypot"
    assert config.postgres_user == "honeypot"
    assert config.postgres_password == "secret"
    assert config.postgres_host == "localhost"
    assert config.postgres_port == 5432