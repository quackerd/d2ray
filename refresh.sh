#!/bin/sh
set -e

chmod 0600 ansible/id_root

for filename in confs/*; do
    addr=$(basename $filename)
    echo "Refreshing $addr..."
    cp docker-compose.yml docker-compose.yml.tmp
    sed -i -E "s/var_hostname/$addr/g" docker-compose.yml.tmp
    ssh -p 77 -o StrictHostKeychecking=no -i ansible/id_root root@$addr -t "mkdir -p /opt/d2ray && \
                                                                                cd /opt/d2ray && \
                                                                                /usr/local/bin/docker-compose down"    
    scp -P 77 -o StrictHostKeychecking=no -i ansible/id_root docker-compose.yml.tmp root@$addr:/opt/d2ray/docker-compose.yml
    scp -P 77 -o StrictHostKeychecking=no -i ansible/id_root $filename root@$addr:/opt/d2ray/config.json
    ssh -p 77 -o StrictHostKeychecking=no -i ansible/id_root root@$addr -t "cd /opt/d2ray && \
                                                                                /usr/local/bin/docker-compose pull &&
                                                                                /usr/local/bin/docker-compose up -d &&
                                                                                docker system prune -a -f"
    
     && /usr/local/bin/docker-compose pull && /usr/local/bin/docker-compose down && /usr/local/bin/docker-compose up -d"
done

wait