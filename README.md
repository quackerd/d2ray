# v2ray-docker
Dockerized v2ray(Websocket + TLS) + Let's Encrypt with official and well-maintained docker containers. No BS private containers.

## Supports:
- v2ray with websocket + TLS protocol using the **official v2ray docker image**.
- Nginx frontend and Let's Encrypt script auto-renewal using the popular **linuxserver/letsencrypt docker image**.

## Usage:
### Required packages
- docker-ce
- docker-compose
- python-jinja2. A popular python template processor. Should be available on most distros' package managers.

### Building
- git clone https://github.com/quackerd/v2ray-docker 
- python setup.py 
