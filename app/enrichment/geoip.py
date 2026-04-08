import time

import requests

from app.honeypot.config import Config


_cache: dict[str, dict] = {}


def _is_private_ip(ip: str) -> bool:
    return ip.startswith(("127.", "10.", "192.168.", "172."))


def enrich_ip(ip: str, config: Config) -> dict | None:
    if _is_private_ip(ip):
        return None

    cached = _cache.get(ip)
    if cached and (time.time() - cached["timestamp"] < config.geoip_cache_ttl_seconds):
        return cached["data"]

    try:
        response = requests.get(
            f"{config.geoip_api_url}/{ip}",
            timeout=config.geoip_timeout_seconds,
        )
        data = response.json()

        if data.get("status") != "success":
            return None

        result = {
            "country": data.get("country", "Unknown"),
            "city": data.get("city", "Unknown"),
            "latitude": data.get("lat"),
            "longitude": data.get("lon"),
        }

        _cache[ip] = {
            "timestamp": time.time(),
            "data": result,
        }
        return result
    except Exception:
        return None