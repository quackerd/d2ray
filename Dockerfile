FROM alpine:latest

ENV VER_XRAY 1.8.3

# install packages
RUN set -xe && apk add --no-cache unzip wget openssl python3 py3-jinja2 supervisor apache2-utils bash

# download packages
RUN set -xe && \
    mkdir -p /downloads && \
    wget -P /downloads https://github.com/XTLS/Xray-core/releases/download/v$VER_XRAY/Xray-linux-64.zip && \
    unzip /downloads/Xray-linux-64.zip -d /opt/xray && \
    rm -rf /downloads

COPY ./opt /opt/

# nginx
# RUN set -xe && addgroup www && \
#     adduser -H -D -S -s /bin/false www -G www && \
#     chown -R www:www /opt/nginx

# remove packages
RUN set -xe && apk del unzip wget
CMD ["sh", "/opt/init.sh"]