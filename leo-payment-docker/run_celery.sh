#!/usr/bin/env bash

VENV=./leo-payment-docker/lvenv

# wait for RabbitMQ server to start
sleep 10

lockfile python.lock
rm -f python.lock

source $VENV/bin/activate

cd src
set -m
# run Celery worker for our project myproject with Celery configuration stored in Celeryconf
su -m root -c "../$VENV/bin/celery worker -f ./log/celery.log -A leopay.celery -Q default -n default@%h" &
su -m root -c "../$VENV/bin/celery flower -A leopay.celery --basic_auth=admin:qwerty12 > ./log/flower.log 2>&1" &
fg %1
