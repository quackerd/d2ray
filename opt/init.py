import os
import getopt
import sys
import subprocess
import jinja2
import random
import string

def parse_comma_str(users : str) -> list[str]:
    return users.split(",")

def build_users_json(users: list[str]) -> str:
    ret : str= ""
    for i in range(len(users)):
        if (i > 0):
            ret = ret + ","
        u = users[i]
        ret = ret + "{ \"id\": \"" + u + "\", \"flow\": \"xtls-rprx-direct\"}"
    return ret

try:
    opts, _ = getopt.getopt(sys.argv[1:], "u:p:f:")
except getopt.GetoptError as err:
    # print help information and exit:
    print(err, flush=True)  # will print something like "option -a not recognized"
    exit(1)

port : int = 443
users : list[str] = [''.join(random.choices(string.ascii_uppercase + string.digits, k=24))]
fqdn : str = "example.com"

for o, a in opts:
    if o == "-u":
        users = parse_comma_str(a)
    elif o == "-p":
        port = int(a)
    elif o == "-f":
        fqdn = a
    else:
        print(f"Unknown option {o}, ignoring...", flush=True)
        exit(1)
print("====== init.py ======", flush=True)
print("Configuration:\n" + \
      f"    port = {port}\n" + \
      f"    fqdn = {fqdn}\n" + \
      f"    users = {str(users)}", flush=True)

print(f"Checking certs for {fqdn}...", flush=True)
if (os.path.exists(f"/etc/letsencrypt/live/{fqdn}")):
    print("Found existing certs, trying to renew...", flush=True)
    subprocess.check_call(f"certbot renew", shell=True)
else:
    print("Unable to locate certs, generating...", flush=True)
    subprocess.check_call(f"certbot certonly -n --standalone -m dummy@dummy.com --agree-tos --no-eff-email -d {fqdn}", shell=True)

jinja_dict : dict[str,str] = dict()
jinja_dict["USERS"] = build_users_json(users)
jinja_dict["PORT"] = str(port)
jinja_dict["FQDN"] = str(fqdn)

print(f"Processing Xray config files...", flush=True)
with open("/opt/xray/d2ray.json.in", "r") as f:
    with open("/opt/xray/d2ray.json", "w") as d:
        template : jinja2.Template = jinja2.Template(f.read())
        d.write(template.render(**jinja_dict))

print(f"Processing Nginx config files...", flush=True)
with open("/opt/nginx/nginx.conf.in", "r") as f:
    with open("/opt/nginx/nginx.conf", "w") as d:
        template : jinja2.Template = jinja2.Template(f.read())
        d.write(template.render(**jinja_dict))
for u in users:
    subprocess.check_call(f"htpasswd -b /opt/nginx/.htpasswd {u} {u}", shell=True)

exit(0)