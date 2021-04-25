FROM alpine:latest

COPY image/ /opt/

RUN set -xe && \
    apk add --no-cache unzip wget nginx certbot openssl && \
    mkdir -p /opt/xray && \
    ln -s /opt/config/certs /etc/letsencrypt && \
    unzip /opt/Xray-linux-64.zip -d /opt/xray && \
    rm /opt/Xray-linux-64.zip && \
    chmod +x /opt/run.sh /opt/crypt.sh && \
    mv /opt/crontab /var/spool/cron/crontabs/root && \
    addgroup www && \
    adduser -H -D -S -s /bin/false www -G www && \
    chown -R www:www /opt/nginx && \
    apk del unzip wget

EXPOSE 80 443

CMD ["/opt/run.sh"]