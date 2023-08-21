[![Build Status](https://ci.quacker.org/api/badges/d/d2ray/status.svg)](https://ci.quacker.org/d/d2ray)
# Xray + xtls-vision + reality all in Docker!
## What Is d2ray?
d2ray is a single Docker container that provides easy 5-minute setups and braindead configurations for xtls-vision + reality.

## Quickstart
1. You can start with the example `docker-compose.yml` from this repo.
2. Adjust environment variables:
    - `PORT`: the port Xray listens on.
    - `TARGET_URL`: the target domain to redirect non proxy connections.
    - `TARGET_PORT`: the target port to redirect non proxy connections.
    - `USERS`: comma separated list of usernames that can access Xray.
    - `LOG_LEVEL`: the verbosity of Xray logs. Default: `warn`.
3. `docker compose up -d`
4. Test your connection.

## Docker Volume
All d2ray logs and private/public key pairs are stored in `/etc/d2ray` in the container. You can mount an external folder to that location to persist settings. See the example `docker-compose.yml`.

## Key Generation
d2ray checks whether a key file exists at path `/etc/xray/certs/keys` and generates a new key pair if not found.

You can either supply a pre-generated private key using `xray x25519` or let d2ray generate one. The corresponding public key is printed to the container log (`docker logs`), which clients use to connect. 

If you are generating the private key yourself, the key file must contain exactly the output of `xray x25519`.

## How To Update?
- `docker compose down`
- `docker compose pull`
- `docker compose up -d`

## Notes
- The old xtls-vision + TLS + Nginx fallback has been branched out to `vision` branch.