FROM alpine:latest


ENV VERSION=var_VERSION
ENV URL https://github.com/XTLS/Xray-core/releases/download/v${VERSION}/Xray-linux-64.zip

COPY ./run.sh /opt/run.sh

RUN set -xe && \
    apk add --no-cache unzip wget nginx certbot openssl && \
    wget ${URL} && \
    mkdir -p /opt/xray && \
    unzip Xray-linux-64.zip -d /opt/xray && \
    rm Xray-linux-64.zip && \
    mkdir -p /opt/config && \
    mkdir -p /opt/config/logs && \
    mkdir -p /opt/config/certs && \
    mkdir -p /opt/config/logs/nginx && \
    mkdir -p /opt/config/logs/xray && \
    mkdir -p /opt/config/logs/crond && \
    chmod +x /opt/run.sh && \
    apk del unzip wget
    
COPY ./nginx.conf /opt/nginx.conf
COPY ./crontab /var/spool/cron/crontabs/root

EXPOSE 80
EXPOSE 443

CMD ["/opt/run.sh"]
