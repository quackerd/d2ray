import os
import getopt
import sys
import subprocess
import jinja2
import random
import string

def process_directory(path : str, vars : dict[str, str], delete_template : bool = True) -> None:
    for f in os.listdir(path):
        full_path = os.path.join(path, f)
        if os.path.isdir(full_path):
            process_directory(full_path, vars, delete_template)
        elif f.endswith(".in"):
            with open(full_path, "r") as sf:
                with open(full_path[:-3], "w") as df:
                    template : jinja2.Template = jinja2.Template(sf.read())
                    df.write(template.render(**vars))
                    print(f"Processed template {full_path}.", flush=True)
            if delete_template:
                subprocess.check_call(f"rm {full_path}", shell=True)


def parse_user_flow(s : str) -> list[tuple[str,str]]:
    users = []
    userconfs : list[str] = s.split(",")
    for userconf in userconfs:
        if len(userconf) == 0:
            continue
        ele = userconf.split("@")
        username = ele[0]
        if (len(ele) > 1):
            flow = ele[1]
        else:
            flow = "xtls-rprx-vision"
        users.append((username, flow))
    return users


def build_users_json(users: list[tuple[str, str]]) -> str:
    ret : str= ""
    for i in range(len(users)):
        if (i > 0):
            ret = ret + ","
        ret = ret + "{\"id\": \"" + users[i][0] + "\",\"flow\": \"" + users[i][1] + "\"}"
    return ret

NGINX_LOCATION_TEMPLATE = '''
    	location /{{ USER }} {
			root /opt/nginx;
			autoindex on;
		}
'''

def build_nginx_locations(users: list[tuple[str, str]]) -> str:
    ret = ""
    for user in users:
        ret += jinja2.Environment().from_string(NGINX_LOCATION_TEMPLATE).render(USER = user[0]) + "\n"
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
        users = parse_user_flow(a)
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
jinja_dict["XRAY_USERS"] = build_users_json(users)
jinja_dict["PORT"] = str(port)
jinja_dict["FQDN"] = str(fqdn)
jinja_dict["NGINX_LOCATIONS"] = build_nginx_locations(users)

print(f"Processing Xray config files...", flush=True)
process_directory("/opt/xray", jinja_dict)

print(f"Processing Nginx config files...", flush=True)
process_directory("/opt/nginx", jinja_dict)

for u in users:
    print(f"Preparing directory for user {u[0]}...", flush=True)
    user_dir = f"/opt/nginx/{u[0]}"
    subprocess.check_call(f"mkdir -p {user_dir}", shell=True)
    subprocess.check_call(f"cp -r /opt/user/* {user_dir}/", shell=True)

    jinja_dict["USER"] = u[0]
    jinja_dict["FLOW"] = u[1]
    process_directory(user_dir, jinja_dict)
    subprocess.check_call(f"ln -sf /downloads/others {user_dir}/others/downloads", shell=True)
    subprocess.check_call(f"ln -sf /downloads/android {user_dir}/android/downloads", shell=True)

exit(0)