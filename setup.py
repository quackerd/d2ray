import getopt
import sys
import uuid
import pwd
import jinja2
import random
import os
import string

def randomString(stringLength=16):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def read_conf(f):
    ret = {}
    f = open(f, "r")
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        eline = line.split(' ')
        if len(eline) >= 2:
            ret[eline[0]] = eline[1]
    return ret

def usage():
    print("Usage: python setup.py [options]\n\n\
    options:\n\
        -h : show usage.\n\
        -d domain : your domain - mydomain.tld.\n\
        [-u uuid] : the uuid of the user. Optional.\n\
        [-p path] : the path of the websocket. Optional.\n\
        [-s subdomain] : your subdomain. Optional.\n\
        [-e email] : your email. Optional.\n\
        [-c conf] : load config from file. Optional.\n\n")

def main():
    email = None
    subdomain = None
    domain = None
    conf_file = None
    uid = os.getuid()
    gid = os.getgid()
    v_uuid = None
    v_path = None

    try:
        opts , _ = getopt.getopt(sys.argv[1:], "hd:s:e:c:u:p:")
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(1)
    
    for o, a in opts:
        if o == "-h":
            usage()
            sys.exit(0)
        elif o == "-d":
            if domain != None:
                print("Can specify maximum ONE domain.")
                sys.exit(1)
            else:
                domain = a
        elif o == "-s":
            if subdomain != None:
                print("Can specify maximum ONE subdomain.")
                sys.exit(1)
            else:
                subdomain = a
        elif o == "-e":
            if email != None:
                print("Can specify maximum ONE email.")
            else:
                email = a
        elif o == "-c":
            conf_file = a
        elif o == "-u":
            v_uuid = a
        elif o == "-s":
            v_path = a

    # overwrite stuff with conf file
    conf = read_conf(conf_file)
    
    if "d" in conf:
        domain = conf["d"]
    if "s" in conf:
        subdomain = conf["s"]
    if "e" in conf:
        email = conf["e"]
    if "u" in conf:
        v_uuid = conf["u"]
    if "p" in conf:
        v_path = conf["p"]
    
    # generate settings if not specified
    if v_uuid == None:
        v_uuid = uuid.uuid4()

    if v_path == None:
        v_path = randomString()

    if domain == None:
        print("Must specify a domain.")
        sys.exit(1)

    server_name = None
    if subdomain == None:
        server_name = domain
    else:
        server_name = subdomain + "." + domain

    # process docker-compose
    with open("docker-compose.yml", "r") as file:
        template = jinja2.Template(file.read())
        
    output = template.render(uid = uid, gid = gid, domain = domain, \
                    subdomain = (subdomain if subdomain != None else ""), \
                    only_sub = ("true" if subdomain != None else "false"), \
                    email = ("dummy@dummy.com" if email == None else email))

    with open("docker-compose.yml", "w") as file:
        file.write(output)

    # process v2ray/config
    with open("v2ray/config.json", "r") as file:
        template = jinja2.Template(file.read())
    
    output = template.render(uuid = v_uuid, path = v_path)

    with open("v2ray/config.json", "w") as file:
        file.write(output)

    # process nginx/nginx/site-confs/default
    with open("nginx/nginx/site-confs/default", "r") as file:
        template = jinja2.Template(file.read())
    
    output = template.render(server_name = server_name, path = v_path)

    with open("nginx/nginx/site-confs/default", "w") as file:
        file.write(output)

    # process client.conf
    with open("client.conf", "r") as file:
        template = jinja2.Template(file.read())

    output = template.render(uuid = v_uuid, path = v_path, server_name = server_name)

    with open("client.conf", "w") as file:
        file.write(output)

    print("Processed all files. The detailed client config is written to client.conf.\n" + \
           "    Summary:\n" + \
           "        Server Address: " + server_name + "\n" \
           "        Path: " + v_path + "\n" \
           "        UUID: " + str(v_uuid) + "\n" \
           "Please run docker-compose up -d to start the service.")

main()
