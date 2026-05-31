FROM alpine:latest

# install packages
RUN apk add --no-cache python3 py3-jinja2 libqrencode-tools s6-overlay

RUN addgroup -g 1000 -S docker && \
    adduser -u 1000 -G docker -S docker

# download packages
RUN <<'EOF'
set -euo pipefail

apk add --no-cache --virtual .build-deps unzip curl jq wget

mkdir -p /opt/xray
JSON=$(curl -fsSL https://api.github.com/repos/XTLS/Xray-core/releases/latest)
DOWNLOAD_URL=$(printf '%s' "$JSON" | jq -r '.assets[] | select(.name | endswith("Xray-linux-64.zip")) | .browser_download_url')
wget -q -O /tmp/xray.zip "${DOWNLOAD_URL}"
unzip /tmp/xray.zip -d /opt/xray
rm /tmp/xray.zip

XRAY_VERSION=$(printf '%s' "$JSON" | jq -r '.tag_name')
printf '%s\n' "$XRAY_VERSION" > /opt/xray/XRAY_VERSION

JSON=$(curl -fsSL https://api.github.com/repos/Loyalsoldier/v2ray-rules-dat/releases/latest)
DOWNLOAD_URL=$(printf '%s' "$JSON" | jq -r '.assets[] | select(.name | endswith("geoip.dat")) | .browser_download_url')
wget -q -O /opt/xray/geoip.dat "${DOWNLOAD_URL}"

DOWNLOAD_URL=$(printf '%s' "$JSON" | jq -r '.assets[] | select(.name | endswith("geosite.dat")) | .browser_download_url')
wget -q -O /opt/xray/geosite.dat "${DOWNLOAD_URL}"

apk del .build-deps
EOF

COPY ./opt /opt/
RUN chown -R docker:docker /opt/xray

#
# Copy s6 service files
#
COPY --chown=root:root ./s6 /etc/s6-overlay/s6-rc.d/
RUN <<'EOF'
set -euo pipefail

chmod +x /etc/s6-overlay/s6-rc.d/init/up
chmod +x /etc/s6-overlay/s6-rc.d/xray/run
chmod +x /etc/s6-overlay/s6-rc.d/xray-ip/run
EOF

VOLUME /etc/d2ray
ENTRYPOINT ["/init"]