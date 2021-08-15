FROM alpine:latest

COPY image/ /opt/

# install packages
RUN set -xe && apk add --no-cache unzip wget nginx certbot openssl

# setup core files
RUN set -xe && mkdir -p /opt/xray && \
    unzip /opt/Xray-linux-64.zip -d /opt/xray && \
    rm /opt/Xray-linux-64.zip && \
    chmod +x /opt/run.sh /opt/crypt.sh

# crond
# RUN set -xe && mv /opt/crontab /var/spool/cron/crontabs/root

# nginx
RUN set -xe && addgroup www && \
    adduser -H -D -S -s /bin/false www -G www && \
    chown -R www:www /opt/nginx

# remove packages
RUN set -xe && apk del unzip wget

EXPOSE 80 443

CMD ["/opt/run.sh"]