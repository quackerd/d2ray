#!/bin/sh

decrypt()
{
    input=$1
    key=$2
    crypt_ret=$(echo $input | openssl enc -d -salt -aes-256-cbc -a -md sha512 -pbkdf2 -pass pass:$key)
}

encrypt()
{
    input=$1
    key=$2
    crypt_ret=$(echo $input | openssl enc -e -salt -aes-256-cbc -a -A -md sha512 -pbkdf2 -pass pass:$key)
}

hash_sha256()
{
    input=$1$2
    crypt_ret=$(echo $input | openssl dgst -sha256 | sed -E "s/\(stdin\)= (.*)/\1/g")
}