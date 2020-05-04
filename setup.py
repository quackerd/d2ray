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

def usage():
    print("Usage: python setup.py [options]\n\n\
    options:\n\
        -h : show usage.\n\
        -d domain : your domain - mydomain.tld.\n\
        [-s subdomain] : your subdomain. Optional.\n\
        [-e email] : your email. Optional.\n")

def main():
    email = None
    subdomain = None
    domain = None
    uid = os.getuid()
    gid = os.getgid()
    v_uuid = uuid.uuid4()
    v_path = randomString()

    try:
        opts , args = getopt.getopt(sys.argv[1:], "hd:s:e:")
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
