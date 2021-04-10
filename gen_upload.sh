#!/bin/sh

set +e

SALT="md5md5"

mkdir -p ./uploads

for filename in ./confs/*; do
    fname=$(basename $filename)
    echo $fname
    fhash=$(echo -n '$fname.$SALT' | openssl dgst -md5 | sed -E 's/\(stdin\)= (.*)/\1/')
    openssl aes-256-cbc -md sha512 -pbkdf2 -in $filename -out ./uploads/$fhash.conf -k "sergeygorbunov"
done