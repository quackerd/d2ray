import os
import subprocess
import jinja2
import random
import string
import pathlib

CONFIG_DIR = pathlib.Path("/etc/d2ray")
KEY_FILE = CONFIG_DIR.joinpath("certs/keys")
LOG_DIR = CONFIG_DIR.joinpath("logs")
XRAY_BIN = pathlib.Path("/opt/xray/xray")

class d2args:
    port : int
    target_port : int
    target_host : str
    target_sni : str
    log_level : str
    users : list[str]
    def __init__(self) -> None:
        self.port = 443
        self.target_host = "localhost"
        self.target_port = 443
        self.target_sni = "localhost"
        self.log_level = "warn"
        self.users = [''.join(random.choices(string.ascii_uppercase + string.digits, k=24))]

    def from_env(self) -> None:
        env = os.getenv("PORT")
        if env != None:
            self.port = int(env)

        env = os.getenv("TARGET_PORT")
        if env != None:
            self.target_port = int(env)  

        env = os.getenv("TARGET_SNI")
        if env != None:
            self.target_sni = env.split(",")
        
        env = os.getenv("TARGET_HOST")
        if env != None:
            self.target_host = env

        env = os.getenv("LOG_LEVEL")
        if env != None:
            self.log_level = env        

        env = os.getenv("USERS")
        if env != None:
            self.users = env.split(",")

    def __str__(self):
        ret = (f"Port: {self.port}\n"
               f"Target Port: {self.target_port}\n"
               f"Target Host: {self.target_host}\n"
               f"Target SNI: {', '.join(self.target_sni)}\n"
               f"Log Level: {self.log_level}\n"
               f"Users: {', '.join(self.users)}"
        )
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

def build_target_snis(snis : list[str]) -> str:
    return ', '.join(['"' + item + '"' for item in snis])

def build_users_json(users: list[str]) -> str:
    return ', '.join(["{\"id\": \"" + item + "\", \"flow\": \"xtls-rprx-vision\"}" for item in users])

def build_jinja_dict(args : d2args, skey : str) -> dict[str, str]:
    jinja_dict : dict[str,str] = dict()
    jinja_dict["PORT"] = str(args.port)
    
    jinja_dict["TARGET_HOST"] = args.target_host
    jinja_dict["TARGET_PORT"] = str(args.target_port)
    jinja_dict["TARGET_SNI"] = build_target_snis(args.target_sni)

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
    print(f"Initializing d2ray...", flush=True)
    args = d2args()
    args.from_env()

    print(f"Checking key file...", flush=True)
    if not KEY_FILE.exists():
        print(f"Key file not found at {KEY_FILE}. Generating...")
        out = subprocess.check_output(f"{XRAY_BIN} x25519", shell = True).decode()
        with open(KEY_FILE, "w") as f:
            f.write(out)
    
    with open(KEY_FILE, "r") as f:
        out = f.read()

    print(f"Reading keys...", flush=True)
    skey, pkey = parse_xray_x25519_output(out)

    print(f"Verifying public key...", flush=True)
    _, _pkey = parse_xray_x25519_output(subprocess.check_output(f"{XRAY_BIN} x25519 -i {skey}", shell = True).decode())
    if (_pkey != pkey):
        print(f"Unmatching public key: expected \"{_pkey}\" but key file provided \"{pkey}\". Please verify the key file.", flush=True)

    print(f"\nConfigurations:\n{str(args)}\nPublic key: {pkey}\n", flush=True)

    template = build_jinja_dict(args, skey)

    print(f"Processing config files...", flush=True)
    process_directory("/opt/xray", template)

main()
