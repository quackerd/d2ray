import getopt
import sys
import uuid
import pwd
import jinja2
import random
import os
import string
import yaml

OUTPUT_DIR = "build"
CLIENT_OUTPUT_DIR = "clients"
DEFAULT_EMAIL = "dummy@dummy.org"
CONF_FILE = "config.yml"
SERVER_IN = "server.in"
SERVER_PATH = "v2ray"
SERVER_FN = "config.json"
NGINX_IN = "nginx.in"
NGINX_PATH = "nginx/nginx/site-confs"
NGINX_FN = "default"
DEFAULT_ALTERID = 64
CLIENT_OBJ_IN = "client_obj.in"
CLIENT_CONF_IN = "client_conf.in"
DOCKER_IN = "docker-compose.in"
WATCHTOWER_IN = "watchtower.in"
DEFAULT_WATCHTOWER_ENABLE = False
DEFAULT_CLIENT_PORT = 1080

def yaml_key_exists_else(mapping : [], name : str, other_val = None, nullable = True):
    if (name in mapping) and (mapping[name] != None):
        return mapping[name]
    else:
        if not nullable:
            raise Exception("Key " + name + " must not be null.")
        else:
            return other_val

class Client:
    def __init__(self, conf_obj):
        self.name = str(yaml_key_exists_else(conf_obj, 'name', nullable=False))
        self.id = str(yaml_key_exists_else(conf_obj, 'id', other_val=uuid.uuid4()))
        self.alterid = int(yaml_key_exists_else(conf_obj,'alterid', other_val=DEFAULT_ALTERID))
        self.port = int(yaml_key_exists_else(conf_obj, 'port', other_val=DEFAULT_CLIENT_PORT))
    
    def print(self, ident):
        pre = ""
        for i in range(ident):
            pre += " "

        print(pre + "{")
        print(pre + "   id: " + self.id)
        print(pre + "   alterid: " + str(self.alterid))
        print(pre + "   port: " + str(self.port))
        print(pre + "}")



class Config:
    @staticmethod
    def __randomString(stringLength=16):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    def print(self):
        print("Server configuration:")
        print("    domain: " + self.domain)
        print("    email: " + self.email)
        print("    subdomain: " + self.subdomain)
        print("    uid: " + str(self.uid))
        print("    gid: " + str(self.gid))
        print("    path: " + self.path)
        print("    clients:")
        for i in range(len(self.clients)):
            self.clients[i].print(8)
        
    def __init__(self, f):
        conf = yaml.safe_load(f)
        conf_srv = conf['server']

        self.domain = str(yaml_key_exists_else(conf_srv, 'domain', nullable=False))
        self.email = str(yaml_key_exists_else(conf_srv, 'email', other_val=DEFAULT_EMAIL))
        self.subdomain = str(yaml_key_exists_else(conf_srv, 'subdomain', other_val=""))
        self.subdomain_only = len(self.subdomain) == 0
        self.uid = int(yaml_key_exists_else(conf_srv, 'uid', other_val=os.getuid()))
        self.gid = int(yaml_key_exists_else(conf_srv, 'gid', other_val=os.getgid()))
        self.path = str(yaml_key_exists_else(conf_srv, 'path', other_val=self.__randomString()))
        self.watchtower = bool(yaml_key_exists_else(conf_srv, 'watchtower', other_val=DEFAULT_WATCHTOWER_ENABLE))

        self.clients = []
        conf_clients = conf['clients']
        for i in range(len(conf_clients)):
            self.clients.append(Client(conf_clients[i]))

def main():
    with open(CONF_FILE, 'r') as f:
        conf = Config(f)
    conf.print()

    template_dict = {}
    template_dict['uid'] = conf.uid
    template_dict['gid'] = conf.gid
    template_dict['subdomain'] = conf.subdomain
    template_dict['subdomain_only'] = conf.subdomain_only
    template_dict['domain'] = conf.domain
    template_dict['email'] = conf.email
    template_dict['path'] = conf.path

    if conf.watchtower:
        with open(WATCHTOWER_IN, "r") as f:
            template_dict['watchtower'] = f.read()
    else:
        template_dict['watchtower'] = ""
    
    clients = ""
    with open(CLIENT_OBJ_IN, "r") as f:
        client_obj = f.read()
    for i in range(len(conf.clients)):
        if i > 0:
            clients += ",\n"
        clients += jinja2.Template(client_obj).render(id = conf.clients[i].id, 
                                                            alterid = conf.clients[i].alterid)
    template_dict['clients'] = clients

    print("Generating files...")

    # create output dir
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # generate docker-compose.yml
    path = os.path.join(OUTPUT_DIR, "docker-compose.yml")
    with open(DOCKER_IN, "r") as f:
        template = jinja2.Template(f.read())
    with open(path, "w") as f:
        f.write(template.render(template_dict))
    
    # generate NGINX conf
    with open(NGINX_IN, "r") as f:
        template = jinja2.Template(f.read())
    path = os.path.join(OUTPUT_DIR, NGINX_PATH)
    os.makedirs(path, exist_ok=True)
    path = os.path.join(path, NGINX_FN)
    with open(path, "w") as f:
        f.write(template.render(template_dict))

    # generate v2ray conf
    with open(SERVER_IN, "r") as f:
        template = jinja2.Template(f.read())
    path = os.path.join(OUTPUT_DIR, SERVER_PATH)
    os.makedirs(path, exist_ok=True)
    path = os.path.join(path, SERVER_FN)
    with open(path, "w") as f:
        f.write(template.render(template_dict))
    
    # generate client confs
    path = os.path.join(OUTPUT_DIR, CLIENT_OUTPUT_DIR)
    os.makedirs(path, exist_ok=True)
    with open(CLIENT_CONF_IN, "r") as f:
        client_conf_temp = jinja2.Template(f.read())
    for i in range(len(conf.clients)):
        template_dict['id'] = conf.clients[i].id
        template_dict['port'] = conf.clients[i].port
        template_dict['alterid'] = conf.clients[i].alterid
        epath = os.path.join(path, conf.clients[i].name + "_" + conf.clients[i].id)
        os.makedirs(epath, exist_ok=True)
        with open(os.path.join(epath, SERVER_FN), "w") as f:
            f.write(client_conf_temp.render(template_dict))
    
    # chown
    os.chown(OUTPUT_DIR, conf.uid, conf.gid)
    for dirpath, dirnames, filenames in os.walk(OUTPUT_DIR):
        os.chown(dirpath, conf.uid, conf.gid)
        for fname in filenames:
            os.chown(os.path.join(dirpath, fname), conf.uid, conf.gid)
    print("Please find the generated files in the build directory. To start the stack, run docker-compose up -d in the build directory.")

main()