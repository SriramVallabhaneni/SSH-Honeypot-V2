#!/bin/bash
set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y docker.io docker-compose-v2 git

systemctl enable docker
systemctl start docker

usermod -aG docker ubuntu

mkdir -p /opt
cd /opt

if [ ! -d "${app_dir}" ]; then
  git clone ${repo_url} ${app_dir}
else
  cd ${app_dir}
  git pull
fi

cd ${app_dir}

cat > .env <<EOF
APP_ENV=production
LOG_LEVEL=INFO

HONEYPOT_HOST=0.0.0.0
HONEYPOT_PORT=2222
MAX_CONNECTIONS=50
SSH_BANNER=SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5

POSTGRES_DB=honeypot
POSTGRES_USER=honeypot
POSTGRES_PASSWORD=${postgres_password}
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

EXPORTER_PORT=8000
METRICS_REFRESH_SECONDS=15

GEOIP_API_URL=http://ip-api.com/json
GEOIP_TIMEOUT_SECONDS=3
GEOIP_CACHE_TTL_SECONDS=86400
EOF

cd deploy
docker compose up -d --build