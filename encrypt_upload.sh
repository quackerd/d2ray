#!/bin/sh

set -xe

apk add openssh openssl

source image/crypt.sh

mkdir -p enc

for filename in confs/*; do
    basename=$(basename $filename)
    hash_sha256 $basename $(cat ./key)
    output=$crypt_ret
    encrypt "$(cat $filename)" $(cat ./key)
    echo "$crypt_ret" > $output
    scp -P77 -i ansible/id_root $output root@parrot.quacker.org:/dat/apps/nginx/http_dl/root/pub
    rm $output
done
