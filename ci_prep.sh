#!/bin/sh

set -e


apk add openssh openssl wget unzip zip apache2-utils

source image/crypt.sh

chmod 600 ./id_root

# versions
VER_XRAY=1.6.0
VER_SO=2.5.20
VER_NG=1.7.20

# upload files
for filename in confs/*; do
    basename=$(basename $filename)
    hash_sha256 $basename $(cat ./key)
    output=$crypt_ret
    encrypt_file $filename $(cat ./key) $output
    scp -P77 -o StrictHostKeychecking=no -i ./id_root $output root@parrot.quacker.org:/dat/apps/nginx/http_dl/root/pub
    rm $output
done

# build zip
URL_SO=https://github.com/FelisCatus/SwitchyOmega/releases/download/v$VER_SO/SwitchyOmega_Chromium.crx
wget $URL_SO -O SwitchyOmega_Chromium.zip
mkdir zip/chrome
unzip ./SwitchyOmega_Chromium.zip -d zip/chrome || true

URL_NG=https://github.com/2dust/v2rayNG/releases/download/$VER_NG/v2rayNG_"$VER_NG"_arm64-v8a.apk
wget $URL_NG -P image/nginx/download/android/

URL_XRAY_WIN=https://github.com/XTLS/Xray-core/releases/download/v$VER_XRAY/Xray-windows-64.zip
wget $URL_XRAY_WIN
unzip Xray-windows-64.zip -d zip/windows

URL_XRAY_MAC=https://github.com/XTLS/Xray-core/releases/download/v$VER_XRAY/Xray-macos-64.zip
wget $URL_XRAY_MAC
unzip Xray-macos-64.zip -d zip/macos

URL_XRAY_LINUX=https://github.com/XTLS/Xray-core/releases/download/v$VER_XRAY/Xray-linux-64.zip
wget $URL_XRAY_LINUX -P image/

cd zip
zip -r -D ../windows_macos.zip .
cd ..
mv windows_macos.zip image/nginx/download/

# build htpassword
touch .htpasswd
htpasswd -b ./.htpasswd liangyifang liangyifang
htpasswd -b ./.htpasswd ruyuechun ruyuechun
htpasswd -b ./.htpasswd liuxiangdong liuxiangdong
htpasswd -b ./.htpasswd zhoubowen zhoubowen
htpasswd -b ./.htpasswd gaoyuchen gaoyuchen
htpasswd -b ./.htpasswd quackerd quackerd
htpasswd -b ./.htpasswd yushengde yushengde
htpasswd -b ./.htpasswd ivansun ivansun
encrypt_file ./.htpasswd "$(cat ./key)" image/htpasswd
