#!/bin/sh

set +e

BUCKET_NAME="config.quacker.net"

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

BUCKET_HASH=$(echo -n "$BUCKET_NAME" | openssl dgst -md5 | sed -E 's/\(stdin\)= (.*)/\1/')
echo "BUCKET_HASH= $BUCKET_HASH"

echo "===== Setting Up Environment ======"
ln -s /opt/config/certs /etc/letsencrypt

echo "===== Checking Certificates ===="
if [ ! -d "/etc/letsencrypt/live/$FQDN" ]; then
    echo "Generating new certificates..."
    certbot certonly -n --standalone -m dummy@dummy.com --agree-tos --no-eff-email -d "$FQDN"
else
    echo "Certificate exists. Checking renewal..."
    certbot renew
fi

echo "===== Downloading configuration file ====="
hash=$(echo -n "$FQDN.$SALT" | openssl dgst -sha256 | sed -E 's/\(stdin\)= (.*)/\1/')
echo "Host hash is $hash"
wget http://$BUCKET_HASH.s3-website-us-west-1.amazonaws.com/config/$hash.conf -P /opt/
openssl aes-256-cbc -d -md sha512 -pbkdf2 -in /opt/$hash.conf -out /opt/$FQDN.conf -k $KEY

echo "===== Starting services ====="
crond -L /opt/config/logs/crond/log.txt
nginx -c /opt/nginx.conf

echo "===== Starting xray ====="
/opt/xray/xray -c /opt/$FQDN.conf
