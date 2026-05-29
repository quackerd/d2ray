# Xray + Vision + REALITY all in Docker!
[![Build](https://git.quacker.org/d/d2ray/badges/workflows/build.yml/badge.svg?branch=master&label=build)](https://git.quacker.org/d/d2ray/actions)
## What Is d2ray?
d2ray is a single Docker container that provides easy 5-minute setups and braindead configurations for xtls-vision + reality. d2ray is automatically built weekly form the latest [Xray-core](https://github.com/xtls/xray-core) and [geo files](https://github.com/Loyalsoldier/v2ray-rules-dat).

## Quickstart
1. You can start with the example `docker-compose.yml` from this repo.
2. Adjust environment variables:
    - `HOST`: the hostname/IP of the server. `REQUIRED`.
    - `PORT`: the external port Xray listens on. Xray inside the container always listens on 8443 so map your external port to 8443 inside the container.  `Optional, default = 443`.
    - `TARGET_HOST`: the target host to redirect non proxy connections. `Required`.
    - `TARGET_PORT`: the target port to redirect non proxy connections. `Optional, default = 443`.
    - `BLOCK_CN`: blocks all connections to CN IPs & domains. `Optional, default = true`.
    - `BLOCK_ADS`: blocks all connections to Ad IPs & domains. `Optional, default = true`.
    - `BLOCK_LOCAL`: blocks private IPs. `Optional, default = true`.
    - `PRIVATE_KEY` : server's private key. `Optional`.
    - `USERS`: comma separated list of usernames that can access Xray. `Required`.
    - `LOG_LEVEL`: the verbosity of Xray logs. `Optional, default = warning`.
3. `docker compose up -d`
4. Check the container log using `docker logs` for per user shareable links and QR codes supported by most Xray apps. These can also be found under `/etc/xray/users/[USERNAME]` folders.
5. Test your connection.

## Docker Volume
The logs and private key are stored in `/etc/d2ray` in the container. You can mount an external folder to that location to persist settings. Otherwise d2ray creates an anonymous Docker volume.

## Key Generation
If `PRIVATE_KEY` is provided, d2ray uses that key. Otherwise, d2ray generates a new key pair and persists it in `/etc/xray/certs/keys`. The corresponding public key is always printed to the container log, which clients use to connect.

To make d2ray regenerate a new key pair, manually delete the key file `/etc/xray/certs/keys` from the mounted volume.

## How To Update?
- `docker compose down`
- `docker compose pull`
- `docker compose up -d`

## Notes
- The old xtls-vision + TLS + Nginx fallback has been branched out to the `vision` branch.