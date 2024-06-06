FROM alpine:latest

ENV VER_XRAY 1.8.13

# install packages
RUN set -xe && apk add --no-cache unzip wget openssl python3 py3-jinja2 supervisor apache2-utils bash libqrencode libqrencode-tools

# download packages
RUN set -xe && \
    mkdir -p /downloads && \
    wget -P /downloads https://github.com/XTLS/Xray-core/releases/download/v$VER_XRAY/Xray-linux-64.zip && \
    unzip /downloads/Xray-linux-64.zip -d /opt/xray && \
    rm -rf /downloads

COPY ./opt /opt/

# remove packages
RUN set -xe && apk del unzip wget

VOLUME /etc/d2ray
CMD ["sh", "/opt/init.sh"]