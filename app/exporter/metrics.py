from prometheus_client import Gauge


total_attempts = Gauge(
    "honeypot_total_attempts",
    "Total number of connection attempts",
)

unique_ips = Gauge(
    "honeypot_unique_ips",
    "Number of unique attacker IPs",
)

total_credentials = Gauge(
    "honeypot_total_credentials",
    "Total number of credential attempts",
)

def update_metrics(repo):
    total_attempts.set(repo.get_total_attempts())
    unique_ips.set(repo.get_unique_ips())
    total_credentials.set(repo.get_total_credentials())