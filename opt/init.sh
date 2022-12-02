#!/bin/sh
# create log directories
mkdir -p /etc/d2ray/logs/cron
mkdir -p /etc/d2ray/logs/xray
mkdir -p /etc/d2ray/logs/nginx
mkdir -p /etc/d2ray/logs/supervisor

python3 /opt/init.py -p $PORT -u $USERS -f $FQDN
retval=$?
if [ $retval -ne 0 ]; then
    exit $retval
fi
exec /usr/bin/supervisord -c /opt/supervisord.conf