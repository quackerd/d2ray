#!/bin/sh

set +xe

mkdir -p /opt/config
mkdir -p /opt/config/logs
mkdir -p /opt/config/certs
mkdir -p /opt/config/logs/nginx
mkdir -p /opt/config/logs/xray
mkdir -p /opt/config/logs/crond

BUCKET_HASH=3bd6b2ce5101e791b665d709aa8518ce

echo ""
echo "===== Checking Environment Variables ====="
if [ -z "$FQDN" ]; then
    echo "FQDN must be set"
    exit 1
else
    echo "FQDN = $FQDN"
fi

if [ -z "$SALT" ]; then
    echo "SALT must be set"
    exit 1
else
    echo "SALT = $SALT"
fi

if [ -z "$KEY" ]; then
    echo "KEY must be set"
    exit 1
else
    echo "KEY = $KEY"
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
echo "===== Downloading configuration file ====="
hash=$(echo -n "$FQDN.$SALT" | openssl dgst -md5 | sed -E 's/\(stdin\)= (.*)/\1/')
echo "Host hash is $hash"
wget http://$BUCKET_HASH.s3-website-us-west-1.amazonaws.com/config/$hash.conf -O /opt/$hash.conf
openssl aes-256-cbc -d -md sha512 -pbkdf2 -in /opt/$hash.conf -out /opt/$FQDN.json -k $KEY

echo ""
echo "===== Starting services ====="
crond -L /opt/config/logs/crond/log.txt
nginx -c /opt/nginx.conf

echo ""
echo "===== Starting xray ====="
/opt/xray/xray -c /opt/$FQDN.json
