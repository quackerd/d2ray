[![Build Status](https://ci.quacker.org/api/badges/d/d2ray/status.svg)](https://ci.quacker.org/d/d2ray)
# Xray + xtls-vision + reality all in Docker!
## What Is d2ray?
d2ray is a single Docker container that provides easy 5-minute setups and braindead configurations for xtls-vision + reality.

## Quickstart
1. You can start with the example `docker-compose.yml` from this repo.
2. Adjust environment variables:
    - `HOST`: the hostname/IP of the server. `REQUIRED`.
    - `PORT`: the port Xray listens on. `Optional, default = 443`.
    - `TARGET_HOST`: the target host to redirect non proxy connections. `Required`.
    - `TARGET_PORT`: the target port to redirect non proxy connections. `Optional, default = 443`.
    - `TARGET_SNI`: comma separated list of the target website's SNIs. `Required`.
    - `PRIVATE_KEY` : server's private key. `Optional`.
    - `USERS`: comma separated list of usernames that can access Xray. `Required`.
    - `LOG_LEVEL`: the verbosity of Xray logs. `Optional, default = warn`.
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