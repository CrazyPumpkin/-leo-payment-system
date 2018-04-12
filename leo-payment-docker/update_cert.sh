#!/bin/bash

HOME_DIR=/opt/leo-payment-system
CONTAINER_DIR=/app/leo-payment-system
DOMAIN=leopay.leotrado.ru
EMAIL=usermail@gmail.com

mkdir -p /tmp/letsencrypt

docker run \
    -v $HOME_DIR:$CONTAINER_DIR \
    -v $HOME_DIR/leo-payment-docker/nginx/ssl/letsencrypt:/etc/letsencrypt  \
    -v /tmp/letsencrypt:/var/log/letsencrypt \
    -ti certbot/certbot \
      certonly \
      --email $EMAIL \
      --agree-tos \
      --webroot \
      --webroot-path $CONTAINER_DIR/leo-payment-docker/nginx/wellknown/ \
      --no-eff-email  \
      -d $DOMAIN


# --staging
