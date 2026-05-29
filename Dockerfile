FROM alpine:latest

RUN addgroup -g 1000 -S docker && \
    adduser -u 1000 -G docker -S docker

# install packages
RUN <<EOF
set -xe
apk add --no-cache python3 py3-jinja2 libqrencode-tools su-exec
EOF

# download packages
RUN <<EOF
set -xe

apk add --no-cache unzip curl jq wget

mkdir -p /opt/xray
JSON=$(curl -s https://api.github.com/repos/XTLS/Xray-core/releases/latest)
DOWNLOAD_URL=$(printf '%s' "$JSON" | jq -r '.assets[] | select(.name | endswith("Xray-linux-64.zip")) | .browser_download_url')
wget -q -O /tmp/xray.zip "${DOWNLOAD_URL}"
unzip /tmp/xray.zip -d /opt/xray
rm /tmp/xray.zip

XRAY_VERSION=$(printf '%s' "$JSON" | jq -r '.tag_name')
printf '%s\n' "$XRAY_VERSION" > /opt/xray/XRAY_VERSION

JSON=$(curl -s https://api.github.com/repos/Loyalsoldier/v2ray-rules-dat/releases/latest)
DOWNLOAD_URL=$(printf '%s' "$JSON" | jq -r '.assets[] | select(.name | endswith("geoip.dat")) | .browser_download_url')
wget -q -O /opt/xray/geoip.dat "${DOWNLOAD_URL}"

DOWNLOAD_URL=$(printf '%s' "$JSON" | jq -r '.assets[] | select(.name | endswith("geosite.dat")) | .browser_download_url')
wget -q -O /opt/xray/geosite.dat "${DOWNLOAD_URL}"

apk del unzip curl wget jq
EOF

COPY ./opt /opt/
RUN chown -R docker:docker /opt/xray

VOLUME /etc/d2ray
CMD ["sh", "/opt/init.sh"]