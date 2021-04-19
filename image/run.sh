#!/bin/sh

set +xe

mkdir -p /opt/config
mkdir -p /opt/config/logs
mkdir -p /opt/config/certs
mkdir -p /opt/config/logs/nginx
mkdir -p /opt/config/logs/xray
mkdir -p /opt/config/logs/crond

echo ""
echo "===== Checking Environment Variables ====="
if [ -z "$FQDN" ]; then
    echo "FQDN must be set"
    exit 1
else
    echo "FQDN = $FQDN"
fi

echo ""
echo "===== Checking Certificates ===="
if [ ! -d "/etc/letsencrypt/live/$FQDN" ]; then
    echo "Generating new certificates..."
    certbot certonly -n --standalone -m dummy@dummy.com --agree-tos --no-eff-email -d $FQDN
else
    echo "Certificate exists. Checking renewal..."
    certbot renew
fi

echo ""
echo "===== Starting services ====="
crond -L /opt/config/logs/crond/log.txt
nginx -c /opt/nginx.conf

echo ""
echo "===== Starting xray ====="
exec /opt/xray/xray -c /opt/config.json
