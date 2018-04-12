#!/usr/bin/env bash

rm /etc/nginx/conf.d/*
cp /opt/paysys/leo-payment-docker/nginx/* /etc/nginx/conf.d/
mkdir -p /etc/nginx/ssl/
cp /opt/paysys/leo-payment-docker/nginx/ssl/* /etc/nginx/ssl/
nginx -g "daemon off;"
