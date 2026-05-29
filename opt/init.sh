#!/bin/sh
set -euo pipefail

# create directories
mkdir -p /etc/d2ray/logs
mkdir -p /etc/d2ray/certs
rm -rf /etc/d2ray/users

python3 /opt/init.py

chown -R docker:docker /etc/d2ray

exec su-exec docker:docker /opt/xray/xray -c /opt/xray/d2ray.json