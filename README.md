# SSH-Honeypot-V2

A cloud-deployed SSH honeypot platform that captures real-world brute-force attack traffic, stores structured event data, and exposes operational metrics through a full observability stack. Built with Python, Docker, PostgreSQL, Prometheus, Grafana, Terraform, and GitHub Actions.

---

## What It Does

The system exposes a fake SSH service to the internet. Automated scanners and bots attempt to log in — every connection attempt, credential pair, and session fingerprint is captured, enriched with geolocation data, and stored in PostgreSQL. A Prometheus exporter surfaces aggregate attack metrics, which Grafana visualizes in real time.

This is not a pre-built tool. The SSH server, authentication handler, session model, metrics exporter, and enrichment pipeline are all custom-written.

---

## Why It Was Built

This project was designed as a hands-on DevSecOps platform — not just a security experiment, but a system that demonstrates:

- **Security engineering** — custom honeypot with real attack telemetry
- **DevOps** — containerized, reproducible, and automatically deployed
- **Infrastructure-as-code** — full AWS environment provisioned with Terraform
- **Observability** — metrics pipeline from ingestion to dashboards
- **CI/CD** — automated testing, security scanning, and deployment via GitHub Actions

---

## Architecture

```
Internet (SSH brute-force traffic)
        │
        ▼
┌─────────────────────┐
│   SSH Honeypot      │  Python + Paramiko
│   Port 2222         │  Captures connections, credentials, banners
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   PostgreSQL        │  Structured storage
│   connections       │  source_ip, banner, country, duration
│   credentials       │  username, password, connection_id
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Prometheus        │  Scrapes /metrics from exporter
│   Exporter          │  Aggregates DB counts into gauges
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Grafana           │  Dashboards: attempts, unique IPs,
│                     │  credentials, geolocation
└─────────────────────┘

Infrastructure: AWS VPC → Subnet → EC2 → Docker Compose
Provisioning:   Terraform
CI/CD:          GitHub Actions (CI gate → CD deploy)
```

---

## Tech Stack

| Layer | Tools |
|---|---|
| Honeypot | Python, Paramiko |
| Storage | PostgreSQL (psycopg) |
| Observability | Prometheus, Grafana |
| Containerization | Docker, Docker Compose |
| Infrastructure | Terraform, AWS (VPC, EC2, Security Groups, IAM) |
| CI/CD | GitHub Actions |
| Security scanning | Bandit, pip-audit |
| Linting / testing | Ruff, Pytest |

---

## Repository Structure

```
SSH-Honeypot-V2/
├── app/
│   ├── honeypot/         # SSH server, auth handler, session model, config
│   ├── enrichment/       # IP geolocation lookup and caching
│   ├── db/               # PostgreSQL schema init and repository layer
│   ├── exporter/         # Prometheus metrics definitions and HTTP server
│   └── main.py           # Entry point
├── deploy/
│   ├── docker-compose.yml
│   ├── prometheus.yml
│   └── grafana/          # Provisioned datasources and dashboards
├── infra/
│   └── terraform/        # VPC, subnet, IGW, security groups, EC2, IAM
├── tests/                # Unit tests for config, session, geoip
├── .github/
│   └── workflows/
│       ├── ci.yml        # Lint, test, security scan
│       └── cd.yml        # Deploy to EC2 after CI passes
├── .env.example
├── requirements.txt
└── pyproject.toml
```

---

## How It Works

1. The honeypot listens for inbound SSH connections on port 2222 (public-facing)
2. Every connection is accepted; authentication always fails — but usernames, passwords, and session metadata are captured before rejection
3. Each attacker's public IP is enriched with geolocation (country, city, coordinates) via a cached external API call
4. The complete session record is written to PostgreSQL with a foreign-key relationship between connections and credential attempts
5. A Prometheus exporter periodically queries PostgreSQL and exposes aggregate metrics at `/metrics`
6. Prometheus scrapes the exporter on a configurable interval
7. Grafana reads from Prometheus and renders attack activity dashboards

---

## CI/CD Pipeline

```
Push to main
     │
     ▼
┌──────────────────────────────────┐
│ CI (GitHub Actions)              │
│  • Ruff (lint)                   │
│  • Pytest (unit tests)           │
│  • Bandit (static security scan) │
│  • pip-audit (dependency scan)   │
└──────────────┬───────────────────┘
               │ passes
               ▼
┌──────────────────────────────────┐
│ CD (GitHub Actions)              │
│  • SSH into EC2                  │
│  • git pull                      │
│  • docker compose down/up        │
└──────────────────────────────────┘
```

CD only runs if CI passes. Deployment does not happen on a failing build.

---

## Infrastructure (Terraform)

Terraform provisions the complete AWS environment from scratch:

| Resource | Purpose |
|---|---|
| VPC | Isolated network boundary |
| Public subnet | Places EC2 with a reachable public IP |
| Internet Gateway | Enables inbound/outbound internet traffic |
| Route table + association | Routes external traffic through the IGW |
| Security group | Controls port access (honeypot public, monitoring restricted) |
| EC2 instance | Runs the full Docker Compose stack |
| IAM role | Least-privilege instance profile |

The EC2 instance bootstraps itself on first boot via a `user_data` script: installs Docker, clones the repo, writes the runtime `.env`, and starts the stack. No manual setup required after `terraform apply`.

Sensitive values (Postgres password, allowed IPs) are passed through Terraform variables and kept out of the public repository.

---

## Local Setup

**Prerequisites:** Python 3.12+, Docker, Docker Compose

```bash
git clone https://github.com/YOUR_USERNAME/SSH-Honeypot-V2.git
cd SSH-Honeypot-V2

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env with your local values

cd deploy
docker compose up --build
```

Test the honeypot:

```bash
ssh -p 2222 test@localhost
# type any password — the attempt is logged and rejected
```

Check data:

```bash
docker compose exec postgres psql -U honeypot -d honeypot
SELECT * FROM connections ORDER BY timestamp DESC LIMIT 10;
```

---

## AWS Deployment

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

After apply, the instance self-configures and the full stack starts automatically. Access Grafana at `http://<instance-ip>:3000` once containers are running.

---

## Exposed Metrics

| Metric | Description |
|---|---|
| `honeypot_total_attempts` | Total connection attempts recorded |
| `honeypot_unique_ips` | Number of distinct attacker IPs |
| `honeypot_total_credentials` | Total username/password pairs captured |

---

## Security Design

- The honeypot never grants access — all authentication attempts fail by design
- Monitoring ports (Grafana, Prometheus) are restricted to trusted IPs via security group rules
- PostgreSQL is not exposed externally; it is internal to the Docker network
- Credentials and sensitive config are injected via environment variables, not hardcoded
- Intentional public exposure (honeypot) is separated from administrative and observability access
- Static security scanning (Bandit) and dependency auditing (pip-audit) run on every push

---

## Known Limitations and Future Work

- **Port separation:** Honeypot currently runs on port 2222. The intended production layout moves the honeypot to port 22 and restricts real admin SSH to a separate port — this requires reconfiguring the host SSH daemon at bootstrap, which is straightforward but was deferred.
- **GeoIP provider:** The current provider uses HTTP. A future improvement is switching to a provider with HTTPS and a higher rate limit.
- **Private IP detection:** The current check is a simple prefix match. A more robust implementation uses Python's `ipaddress` module to catch all reserved ranges.
- **Alerting:** Prometheus alert rules and Grafana alerts (e.g., for attack spikes or service downtime) are not yet configured.
- **Secret management:** Sensitive values are currently managed through Terraform variables. A more mature setup would use AWS SSM Parameter Store or Secrets Manager.
- **Deployment method:** SSH-based CD is functional but not ideal for production. Future improvement would use AWS SSM or OIDC-based GitHub Actions authentication.

---

## Disclaimer

This project is built for educational and defensive security research purposes. It is intended to observe unsolicited attack activity against a controlled, isolated environment. Do not use this to monitor traffic you are not authorized to capture.