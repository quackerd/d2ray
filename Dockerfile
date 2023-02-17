FROM alpine:latest

ENV VER_XRAY 1.7.5
ENV VER_SO 2.5.20
ENV VER_NG 1.7.38

# install packages
RUN set -xe && apk add --no-cache unzip wget nginx certbot openssl python3 py3-jinja2 supervisor apache2-utils bash

# download packages
RUN set -xe && \
    mkdir -p /downloads /downloads/others /downloads/android && \
    wget -P /downloads/others https://github.com/XTLS/Xray-core/releases/download/v$VER_XRAY/Xray-windows-64.zip && \
    wget -P /downloads/others https://github.com/XTLS/Xray-core/releases/download/v$VER_XRAY/Xray-linux-64.zip && \
    wget -P /downloads/others https://github.com/FelisCatus/SwitchyOmega/releases/download/v$VER_SO/SwitchyOmega_Chromium.crx && \
    wget -P /downloads/android https://github.com/2dust/v2rayNG/releases/download/$VER_NG/v2rayNG_"$VER_NG"_arm64-v8a.apk && \
    wget -P /downloads/others https://github.com/XTLS/Xray-core/releases/download/v$VER_XRAY/Xray-macos-64.zip && \
    wget -P /downloads/others https://github.com/XTLS/Xray-core/releases/download/v$VER_XRAY/Xray-macos-arm64-v8a.zip

COPY ./opt /opt/

# xray
RUN set -xe && unzip /downloads/others/Xray-linux-64.zip -d /opt/xray

# nginx
RUN set -xe && addgroup www && \
    adduser -H -D -S -s /bin/false www -G www && \
    chown -R www:www /opt/nginx

# remove packages
RUN set -xe && apk del unzip wget
EXPOSE 80
VOLUME /etc/letsencrypt
CMD ["sh", "/opt/init.sh"]