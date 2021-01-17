# d2ray
Clean, dockerized v2ray(Websocket + TLS) + Nginx + Let's Encrypt with official and well-maintained docker containers. No BS private containers.

## Supports:
- v2ray with websocket + TLS protocol using the [teddysun/v2ray](https://hub.docker.com/r/teddysun/v2ray).
- Nginx frontend and **auto-renewing** Let's Encrypt certificate using the popular [linuxserver/swag](https://hub.docker.com/r/linuxserver/swag/).
- watchtower for automatic docker image updates (can be disabled) from [containrrr/watchtower](https://hub.docker.com/r/containrrr/watchtower)
- Easy multiuser configuration and user conf file generation.
## Usage:
### Required packages
- python3.
- docker-ce.
- docker-compose.
- python-jinja2. A popular python template processor. Just search for jinja2 with your distro's package manager.

### Building
- Clone this repo.
- Modify `config.yml` to your liking. Please see the comments in the file for documentation.
- Run `configure.py` with python 3.
- Generated files are located in the `build` directory. Run `docker-compose up -d` within that directory to start the stack.
- To start over or to update the existing configuration. Simply change `config.yml`, rerun `configure.py` and restart the stack.

### Client connections
Client conf files are generated in `build/clients/[name]_[uuid]/config.json`. Clients simply need to download the most recent v2ray release and replace `config.json` with the ones generated. The config file by default directly connects to CN mainland websites and proxies foreign websites. The same goes for DNS lookups.

You can customize the template file `client_conf.in` to generate custom client conf files.

### Troubleshooting
- Make sure your subdomain.domain.tld points to the server.
- Use `docker logs v2ray_nginx` to check for nginx init errors. Detailed nginx logs and be found in `nginx/logs/nginx`
- Use `docker logs v2ray_v2ray` to check for v2ray init errors.
- Use `docker logs v2ray_watchtower` to check for watchtower errors.