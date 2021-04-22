#!/bin/sh
set -e

key=$(cat ./key)

for filename in confs/*; do
    addr=$(basename $filename)
    echo "Refreshing $addr..."
    ssh -p 77 -o StrictHostKeychecking=no -i ansible/id_root root@$addr -t "docker pull quackerd/d2ray:latest"
    ssh -p 77 -o StrictHostKeychecking=no -i ansible/id_root root@$addr -t "docker stop d2ray"
    ssh -p 77 -o StrictHostKeychecking=no -i ansible/id_root root@$addr -t "docker run -d \
                                                                         -e KEY=$key \
                                                                         -e FQDN=$addr \
                                                                         -p 80:80 \
                                                                         -p 443:443 \
                                                                         -v d2ray_volume:/opt/config \
                                                                         --name d2ray \
                                                                         quackerd/d2ray:latest"
    ssh -p 77 -o StrictHostKeychecking=no -i ansible/id_root root@$addr -t "docker system prune -af"
done

wait