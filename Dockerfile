FROM alpine:latest

ENV VER_XRAY 1.6.1
ENV VER_SO 2.5.20
ENV VER_NG 1.7.20

# install packages
RUN set -xe && apk add --no-cache zip unzip wget nginx certbot openssl python3 py3-jinja2 supervisor apache2-utils bash

COPY ./opt /opt/

# download packages
RUN set -xe && \
    wget -P /opt/zip/windows/ https://github.com/XTLS/Xray-core/releases/download/v$VER_XRAY/Xray-windows-64.zip && \
    mkdir -p /opt/zip/linux && \
    wget -P /opt/zip/linux/ https://github.com/XTLS/Xray-core/releases/download/v$VER_XRAY/Xray-linux-64.zip && \
    mkdir -p /opt/zip/chrome && \
    wget -P /opt/zip/chrome/ https://github.com/FelisCatus/SwitchyOmega/releases/download/v$VER_SO/SwitchyOmega_Chromium.crx && \
    wget -P /opt/zip/android/ https://github.com/2dust/v2rayNG/releases/download/$VER_NG/v2rayNG_"$VER_NG"_arm64-v8a.apk && \
    wget -P /opt/zip/macos/ https://github.com/XTLS/Xray-core/releases/download/v$VER_XRAY/Xray-macos-64.zip && \
    wget -P /opt/zip/macos/ https://github.com/XTLS/Xray-core/releases/download/v$VER_XRAY/Xray-macos-arm64-v8a.zip

# xray
RUN set -xe && unzip /opt/zip/linux/Xray-linux-64.zip -d /opt/xray

# create zip
RUN set -xe && \
            zip -r /opt/d2ray.zip /opt/zip && \
            mv /opt/d2ray.zip /opt/nginx/download/ && \
            rm -r /opt/zip

# nginx
RUN set -xe && addgroup www && \
    adduser -H -D -S -s /bin/false www -G www && \
    chown -R www:www /opt/nginx

# remove packages
RUN set -xe && apk del zip unzip wget
EXPOSE 80
VOLUME /etc/letsencrypt
CMD ["sh", "/opt/init.sh"]