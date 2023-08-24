#!/bin/sh
# create directories
mkdir -p /etc/d2ray/logs/xray
mkdir -p /etc/d2ray/logs/supervisord
mkdir -p /etc/d2ray/certs
rm -rf /etc/d2ray/users

python3 /opt/init.py
retval=$?
if [ $retval -ne 0 ]; then
    exit $retval
fi

exec /usr/bin/supervisord -c /opt/supervisord.conf