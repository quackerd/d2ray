[![Build Status](https://ci.quacker.org/api/badges/d/d2ray/status.svg)](https://ci.quacker.org/d/d2ray)
# Xray + VLESS + XTLS + Nginx fallback in Docker!
## What is d2ray?
d2ray is a single Docker container that provides easy and braindead configuration for Xray + XTLS + Nginx fallback. d2ray also offers currently hardcoded setup instructions and Xray binary packages for various OSes and architectures.

## Features
- Easy 5-minutes setup.
- Automatic generation and renewal of Let's Encrypt SSL certificates.
- Packaged Xray binary on the fallback website.
- Per-user setup instructions for various architectures.

## How to use?
1. Download the `docker-compose.yml` from this repo.
2. Create a `.env` file in the same directory and configure the instance to your liking.
    - See `.env` in the current repo.
    - `PORT`: the port to run Xray on.
    - `FQDN`: the domain name of your server, used to generate SSL certificates.
    - `USERS`: comma separated list of `USERCONF` allowed access to both Xray and resource downloads. Each `USERCONF` is of format `userid@flow`. `userid` is used as the credential for Xray. If `flow` is not specified it defaults to `xtls-rprx-vision`. For example, setting `USERS` to `user1@xtls-rprx-direct,user2` means two users: `user1` with flow `xtls-rprx-direct` and `user2` with flow `xtls-rprx-vision`.
    - `LOGDIR`: the directory to store logs, currently required.
3. `docker compose up -d`
4. You can access the Xray service using an Xray client. You can access the per-user resource downloads by accessing `https://your-domain:your-port`, entering the `userid` in the textbox at the bottom of the page and clicking the `Download` button next to it.

## How to update?
- `docker compose down`
- `docker compose pull`
- `docker compose up -d`

## Notes
1. Port 80 must be available on the host as it is required to obtain SSL certificates.
2. Note the `docker compose` instead of `docker-compose` commands. d2ray is only tested with the newer docker-compose-plugin (install with your distribution's package manager) as opposed to legacy docker-compose.