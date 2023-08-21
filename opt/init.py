import os
import sys
import subprocess
import jinja2
import random
import string
import pathlib

CONFIG_DIR = pathlib.Path("/etc/d2ray")
PRIVKEY = CONFIG_DIR.joinpath("certs/private_key")
PUBKEY = CONFIG_DIR.joinpath("certs/public_key")
LOG_DIR = CONFIG_DIR.joinpath("logs")
XRAY_BIN = pathlib.Path("/opt/xray/xray")

class d2args:
    port : int
    target_port : int
    target_url : str
    log_level : str
    users : list[str]
    def __init__(self) -> None:
        self.port = 443
        self.target_port = 443
        self.target_url = "localhost"
        self.log_level = "warn"
        self.users = [''.join(random.choices(string.ascii_uppercase + string.digits, k=24))]

    def from_env(self) -> None:
        env = os.getenv("PORT")
        if env != None:
            self.port = int(env)

        env = os.getenv("TARGET_PORT")
        if env != None:
            self.target_port = int(env)  

        env = os.getenv("TARGET_URL")
        if env != None:
            self.target_url = env

        env = os.getenv("LOG_LEVEL")
        if env != None:
            self.log_level = env        

        env = os.getenv("USERS")
        if env != None:
            self.users = env.split(",")

    def __str__(self):
        ret = (f"Port: {self.port}\n"
               f"Target Port: {self.target_port}\n"
               f"Target URL: {self.target_url}\n"
               f"Log Level: {self.log_level}\n"
               f"Users: {', '.join(self.users)}"
        )
        return ret

    def get_users_json(self) -> str:
        ret : str= ""
        for i in range(len(users)):
            if (i > 0):
                ret = ret + ","
            ret = ret + "{\"id\": \"" + users[i][0] + "\",\"flow\": \"" + users[i][1] + "\"}"
        return ret


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

def build_target_fqdns(url : str) -> str:
    prefix = "www."
    fqdns = [url, f"{prefix}{url}"]
    if url.startswith(prefix) and len(url) > len(prefix):
        fqdns.append(url[len(prefix):])
    return ', '.join(['"' + item + '"' for item in fqdns])

def build_users_json(users: list[str]) -> str:
    return ', '.join(["{\"id\": \"" + item + "\", \"flow\": \"xtls-rprx-vision\"}" for item in users])

def build_jinja_dict(args : d2args, skey : str) -> dict[str, str]:
    jinja_dict : dict[str,str] = dict()
    jinja_dict["PORT"] = str(args.port)

    jinja_dict["TARGET_URL"] = args.target_url
    jinja_dict["TARGET_PORT"] = str(args.target_port)
    jinja_dict["TARGET_FQDNS"] = build_target_fqdns(args.target_url)

    jinja_dict["LOG_DIR"] = str(LOG_DIR)
    jinja_dict["LOG_LEVEL"] = args.log_level

    jinja_dict["USERS"] = build_users_json(args.users)
    jinja_dict["PRIVATE_KEY"] = skey

    return jinja_dict

def parse_xray_x25519_output(stdout : str) -> tuple[str, str]:
    skey = None
    pkey = None
    lines = stdout.split("\n")
    if len(lines) < 2:
        raise Exception(f"Unknown Xray output format:\n\"{stdout}\"\n")
    
    priv_key_hdr = "Private key: "
    pub_key_hdr = "Public key: "
    for line in lines:
        if line.startswith(priv_key_hdr):
            skey = line[len(priv_key_hdr):]
        elif line.startswith(pub_key_hdr):
            pkey = line[len(pub_key_hdr):]
    if (skey == None) or (pkey == None):
        raise Exception(f"Unable to extract private or public key from Xray output:\n\"{stdout}\"\n")
    return (skey.strip(), pkey.strip())

def main():
    args = d2args()
    args.from_env()

    print("====== init.py ======", flush=True)
    print(f"Checking server private key...", flush=True)
    if not PRIVKEY.exists():
        print(f"Server private key not found at {PRIVKEY}. Generating...")
        skey, _ = parse_xray_x25519_output(subprocess.check_output(f"{XRAY_BIN} x25519", shell = True).decode())
        with open(PRIVKEY, "w") as f:
            f.write(skey)
    
    with open(PRIVKEY, "r") as f:
        skey = f.read().strip()

    print(f"Deriving public key...", flush=True)
    _, pkey = parse_xray_x25519_output(subprocess.check_output(f"{XRAY_BIN} x25519 -i {skey}", shell = True).decode())

    with open(PUBKEY, "w") as f:
        f.write(pkey)

    print(f"\nConfigurations:\n{str(args)}\nPublic key: {pkey}\n", flush=True)

    template = build_jinja_dict(args, skey)

    print(f"Processing config files...", flush=True)
    process_directory("/opt/xray", template)

main()
