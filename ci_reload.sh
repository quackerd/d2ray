#!/bin/sh
set -e

#apk add openssh

key=$(cat ./key)

chmod 600 ./id_root

while read -r line
do
    filename="confs/$line"
    echo "Conf name: $filename"
    addr=$(basename $filename)
    echo "Refreshing $addr..."
    ssh -p 77 -o StrictHostKeychecking=no -i ./id_root root@$addr -t "docker pull quackerd/d2ray:latest"
    set +e
    ssh -p 77 -o StrictHostKeychecking=no -i ./id_root root@$addr -t "docker stop d2ray && docker rm d2ray"
    set -e
    ssh -p 77 -o StrictHostKeychecking=no -i ./id_root root@$addr -t "docker run -d \
                                                                            --restart unless-stopped \
                                                                            -e KEY=$key \
                                                                            -e FQDN=$addr \
                                                                            -p 80:80 \
                                                                            -p 443:8443 \
                                                                            -v d2ray_volume:/opt/config \
                                                                            --name d2ray \
                                                                            quackerd/d2ray:latest"
    ssh -p 77 -o StrictHostKeychecking=no -i ./id_root root@$addr -t "docker system prune -af"
done < ./reload_list

wait