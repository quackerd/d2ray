#!/bin/sh

set -e

source /opt/crypt.sh

mkdir -p /opt/config
mkdir -p /opt/config/logs
mkdir -p /opt/config/certs
mkdir -p /opt/config/logs/nginx
mkdir -p /opt/config/logs/xray
mkdir -p /opt/config/logs/crond

URL='U2FsdGVkX19/qz4kcbpQpJKz/iebXKih1BK3Cp1wGSoEyhLtoyAi0wewP5Tr++FbRLt/EG2f8zDF9cIEuoTLEA=='

echo ""
echo "===== Checking Environment Variables ====="
if [ -z "$FQDN" ]; then
    echo "FQDN must be set"
    exit 1
fi

if [ -z "$KEY" ]; then
    echo "KEY must be set"
    exit 1
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
echo "===== Fetching Configuration ====="
decrypt $URL $KEY
URL=$crypt_ret

echo "Fetching from $URL..."
hash_sha256 $FQDN $KEY
URL=$URL/$crypt_ret
wget $URL -O /opt/$FQDN

echo "Decrypting..."
decrypt_file /opt/$FQDN $KEY /opt/config.json

decrypt_file /opt/htpasswd $KEY /opt/nginx/.htpasswd

echo ""
echo "===== Starting cron ====="
crond -L /opt/config/logs/crond/log.txt

echo ""
echo "===== Starting Nginx ====="
nginx -c /opt/nginx/nginx.conf

echo ""
echo "===== Starting xray ====="
exec /opt/xray/xray -c /opt/config.json
