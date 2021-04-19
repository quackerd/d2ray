FROM alpine:latest


ENV VERSION=var_VERSION
ENV URL https://github.com/XTLS/Xray-core/releases/download/v${VERSION}/Xray-linux-64.zip

COPY image/run.sh /opt/run.sh
COPY image/nginx.conf /opt/nginx.conf
COPY image/crontab /var/spool/cron/crontabs/root
COPY image/wait_for_it.sh /opt/wait_for_it.sh

RUN set -xe && \
    chmod +x /opt/run.sh && \
    mkdir -p /opt/config && \
    mkdir -p /opt/config/logs && \
    mkdir -p /opt/config/certs && \
    mkdir -p /opt/config/logs/nginx && \
    mkdir -p /opt/config/logs/xray && \
    mkdir -p /opt/config/logs/crond && \
    mkdir -p /opt/xray && \
    ln -s /opt/config/certs /etc/letsencrypt && \
    apk add --no-cache unzip wget nginx certbot openssh bash && \
    wget ${URL} && \
    unzip Xray-linux-64.zip -d /opt/xray && \
    rm Xray-linux-64.zip && \
    apk del unzip wget && \
    addgroup www && \
    adduser -H -D -S -s /bin/false www -G www && \
    chown -R www:www /opt/nginx.conf && \
    chmod +x /opt/run.sh /opt/wait_for_it.sh


EXPOSE 80 443

CMD ["/opt/wait_for_it.sh d2ray_nextcloud:80 --timeout=60 --strict -- /opt/run.sh"]
