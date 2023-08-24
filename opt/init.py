import os
import subprocess
import jinja2
import random
import sys
import string
import pathlib

CONFIG_DIR = pathlib.Path("/etc/d2ray")
KEY_FILE = CONFIG_DIR.joinpath("certs/keys")
LOG_DIR = CONFIG_DIR.joinpath("logs")
QR_DIR = CONFIG_DIR.joinpath("users")
XRAY_BIN = pathlib.Path("/opt/xray/xray")

class d2args:
    host : str
    port : int
    target_port : int
    target_host : str
    target_sni : str
    log_level : str
    private_key : str
    public_key : str
    users : list[str]
    def __init__(self) -> None:
        self._from_env()

    @staticmethod
    def _get_env(name : str, default : str = None, required : bool = True) -> str:
        env = os.getenv(name)
        if env == None:
            if required:
                raise Exception(f"Missing environment variable \"{name}\".")
            else:
                return default
        return env

    @staticmethod
    def _parse_xray_x25519_output(stdout : str) -> tuple[str, str]:
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

    def _from_env(self) -> None:
        self.host = self._get_env("HOST")
        self.target_host = self._get_env("TARGET_HOST")
        self.target_sni = self._get_env("TARGET_SNI").split(",")
        self.users = self._get_env("USERS").split(",")

        self.port = int(self._get_env("PORT", default="443", required=False))
        self.target_port = int(self._get_env("TARGET_PORT", default="443", required=False))
        self.log_level = self._get_env("LOG_LEVEL", default="warn", required=False)

        self.private_key = self._get_env("PRIVATE_KEY", default=None, required=False)
        if (self.private_key == None):
            print(f"Private key not provided.", flush=True)
            if not KEY_FILE.exists():
                print(f"Key file {KEY_FILE} not found. Generating new keys...")
                self.private_key, _ = self._parse_xray_x25519_output(subprocess.check_output(f"{XRAY_BIN} x25519", shell = True).decode())
                with open(KEY_FILE, "w") as f:
                    f.write(self.private_key)
            else:
                print(f"Reading from key file {KEY_FILE} ...")
                with open(KEY_FILE, "r") as f:
                   self.private_key = f.read().strip()

        _ , self.public_key = self._parse_xray_x25519_output(subprocess.check_output(f"{XRAY_BIN} x25519 -i {self.private_key}", shell = True).decode())

    def __str__(self) -> str:
        ret = (f"Host: {self.host}\n"
               f"Port: {self.port}\n"
               f"Target Port: {self.target_port}\n"
               f"Target Host: {self.target_host}\n"
               f"Target SNI: {', '.join(self.target_sni)}\n"
               f"Log Level: {self.log_level}\n"
               f"Users: {', '.join(self.users)}\n"
               f"Public Key: {self.public_key}"
        )
        return ret
    
    def get_shareable_links(self) -> dict[str, str]:
        ret = {}
        for user in self.users:
            ret[user] = (f"vless://{user}@{self.host}:{self.port}/?"
                "flow=xtls-rprx-vision&"
                "type=tcp&security=reality&"
                "fp=chrome&"
                f"sni={','.join(self.target_sni)}&"
                f"pbk={self.public_key}#"
                f"{self.host}"
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

def build_jinja_dict(args : d2args) -> dict[str, str]:
    jinja_dict : dict[str,str] = dict()
    jinja_dict["PORT"] = str(args.port)
    
    jinja_dict["TARGET_HOST"] = args.target_host
    jinja_dict["TARGET_PORT"] = str(args.target_port)
    jinja_dict["TARGET_SNI"] = build_target_snis(args.target_sni)

    jinja_dict["LOG_DIR"] = str(LOG_DIR)
    jinja_dict["LOG_LEVEL"] = args.log_level

    jinja_dict["USERS"] = build_users_json(args.users)
    jinja_dict["PRIVATE_KEY"] = args.private_key
    return jinja_dict


def main():
    print(f"Initializing d2ray...", flush=True)
    args = d2args()

    print(f"\nConfiguration:\n{str(args)}\n", flush=True)

    template = build_jinja_dict(args)

    print(f"Processing config files...", flush=True)
    process_directory("/opt/xray", template)

    print(f"Generating shareable links...", flush=True)
    links = args.get_shareable_links()
    
    for user, link in links.items():
        dir = QR_DIR.joinpath(user)
        os.makedirs(str(dir), exist_ok=True)
        linkf = dir.joinpath("link.txt")
        with open(str(linkf), "w") as f:
            f.write(link + "\n")
        subprocess.check_output(f"qrencode -o {str(dir.joinpath('qrcode.png'))} < {linkf}", shell=True)
        print("")
        print(f"User \"{user}\":", flush=True)
        print(f"{link}")
        print(subprocess.check_output(f"qrencode -t ansiutf8 < {linkf}", shell=True).decode())
        print("")

    print(f"Initialization completed.\n", flush=True)

main()
