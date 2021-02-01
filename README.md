# d2ray
Clean, dockerized xray(VLESS + TCP + XTLS) + Nginx + Let's Encrypt with official and well-maintained docker containers. No private containers.

d2ray opens 443 and 80. xray listens on 443 with VLESS fallback to Nginx. Nginx listens on 80 for regular webrequests. Nginx also redirects all HTTP traffic to 443 for HTTPS except for HTTP traffic coming from xray itself.

## Supports:
- xray with VLESS + TCP + XTLS protocol using [teddysun/xray](https://hub.docker.com/r/teddysun/xray/).
- Nginx frontend and **auto-renewing** Let's Encrypt certificate using the popular [linuxserver/swag](https://hub.docker.com/r/linuxserver/swag/).
- watchtower for automatic docker image updates (can be disabled) from [containrrr/watchtower](https://hub.docker.com/r/containrrr/watchtower)
- Easy multiuser configuration and user conf file generation.
## Usage:
### Required packages
- python3: On CentOS 7: `yum install python3`
- docker-ce
- docker-compose
- jinja2: A popular python template processor. Install with `pip3 install jinja2`.
- pyyaml: Python YAML parser. Install with `pip3 install pyyaml`.

### Building
- Clone this repo.
- Modify `config.yml` to your liking. Please see the comments in the file for documentation.
- Run `configure.py` with python 3.
- Generated files are located in the `build` directory. Run `docker-compose up -d` within that directory to start the stack.
- To start over or to update the existing configuration. Simply change `config.yml`, rerun `configure.py` and restart the stack.

### Client connections
Client conf files are generated in `build/clients/[client name]/config.json`. Clients simply need to download the most recent xray release and replace `config.json` with the ones generated. The config file by default directly connects to CN mainland websites and proxies foreign websites. The same goes for DNS lookups.

You can customize the template file `client_conf.in` to generate custom client conf files.

### Updating
Currently you need to merge conflict yourself. Most likely only `config.yml` unless you customized other template files too. An auto script is WIP and for now please do the following:

1. Pull the latest change with `git pull`
2. If there are conflicts, stash your local changes with `git stash`
3. Run `git pull` again
4. Run `git stash pop` to pop your local changes
5. Manually merge the conflicting files
6. Run `git add -u` to mark them as conflict resolved

### Troubleshooting
#### Basics
- Make sure your subdomain.domain.tld points to the server.
- Use `docker logs d2ray_nginx` to check for nginx init errors. Detailed nginx logs and be found in `nginx/logs/nginx`
- Use `docker logs d2ray_xray` to check for v2ray init errors.
- Use `docker logs d2ray_watchtower` to check for watchtower errors.
- xray log files can be found in `build/xray`

#### Q: The nginx container is stuck?
A: Nginx needs to obtain certificate on its first launch so this is sort of expected. If it takes an unusual amount of time (>60 seconds), kindly Ctrl-C to interrupt docker-compose and check the nginx log. Most likely something is misconfigured. 
