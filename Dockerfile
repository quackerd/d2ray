FROM alpine:latest


ENV VERSION=var_VERSION
ENV URL https://github.com/XTLS/Xray-core/releases/download/v${VERSION}/Xray-linux-64.zip

COPY ./run.sh /opt/run.sh
COPY ./nginx /opt/nginx
COPY ./nginx.conf /opt/nginx.conf
COPY ./crontab /var/spool/cron/crontabs/root

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
    apk add --no-cache unzip wget nginx certbot openssl && \
    wget ${URL} && \
    unzip Xray-linux-64.zip -d /opt/xray && \
    rm Xray-linux-64.zip && \
    apk del unzip wget && \
    addgroup www && \
    adduser -H -D -S -s /bin/false www -G www && \
    chown -R www:www /opt/nginx /opt/nginx.conf


EXPOSE 80 443

CMD ["/opt/run.sh"]
