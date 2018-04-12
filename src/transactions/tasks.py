import logging
import os
from pathlib import Path
from random import choice, randint

import requests
import rsa
from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils import timezone
from django_redis import get_redis_connection
from requests import RequestException

from billing.models import CounterAgent
from leopay.celery import app
from .models import Transaction
from .utils import sign_dict

logger = get_task_logger('celery.tasks')  # type: logging.Logger

try:
    priv_key = rsa.PrivateKey.load_pkcs1(
        open(os.path.join(settings.RSA_KEY_HOME, settings.RSA_PAYMENT_PRIV_KEY)).read(),
        format='PEM'
    )
except:
    priv_key = None
    logger.error('Error opening private key {}!'.format(os.path.join(settings.RSA_KEY_HOME, settings.RSA_PAYMENT_PRIV_KEY)))

APP_PATH = (Path(__file__) / "..").absolute()


class FakeResponse:
    RATE = (1, 20)

    def __init__(self):
        self.status_code = choice([200] * self.RATE[0] + [500] * self.RATE[1])
        self.text = str(randint(0, 10 ** 6))


RETRY_TIMEOUT = settings.CELERY_RETRY_TIMEOUT


@app.task(bind=True, max_retries=None)
def check_transaction(self, orderId):
    # Check transaction status via SBERBANK API
    conn = get_redis_connection("default")
    with conn.lock('check_transaction-{}'.format(orderId)) as lock:
        transaction = Transaction.objects.get(paysys_id=orderId)

        # Stop "20 min" task
        if self.request.id != transaction.task_id:
            app.control.revoke(transaction.task_id)

        if transaction.status != Transaction.CREATED:
            # Transaction already finished
            logger.info("[{}] Task trying to process already finished {}, close task"
                        .format(self.request.id, transaction))
            return

        params = {
            'userName': settings.SBERBANK['USERNAME'],
            'password': settings.SBERBANK['PASSWORD'],
            'orderId': orderId,
        }
        try:
            resp = requests.get(settings.SBERBANK['GET_ORDER_STATUS_URL'], params)
        except RequestException as e:
            logger.warning("[{}] ({}) Sberbank return exception {}, retry after {} secs"
                           .format(self.request.id, transaction, e, RETRY_TIMEOUT))
            raise self.retry(exc=e, countdown=RETRY_TIMEOUT)

        transaction.gateway_status = resp.text
        if resp.status_code // 100 != 2:  # not 2** codes
            logger.warning("[{}] ({}) Sberbank return status code {}: {}"
                           .format(self.request.id, transaction, resp.status_code, resp.text[:50]))
            transaction.status = Transaction.FAIL
            transaction.save()
            return

        resp_data = resp.json()
        transaction.status_sber = int(resp_data['OrderStatus'])
        if transaction.status_ok:
            transaction.status = Transaction.SUCCESS
            transaction.timestamp_sber = timezone.now()
            transaction.save()
            task = payment_to_billing.delay(transaction.id)
            logger.info("[{}] {} success. Spawn billing task ({})"
                        .format(self.request.id, transaction, task.id))
            return
        elif transaction.status_pending:
            transaction.save()
            logger.info("[{}] {} is not completed yet, retry after {} secs"
                        .format(self.request.id, transaction, RETRY_TIMEOUT))
            raise self.retry(countdown=RETRY_TIMEOUT)
        elif transaction.status_fail:
            transaction.status = Transaction.FAIL
            transaction.save()
            logger.info("[{}] {} fail"
                        .format(self.request.id, transaction))
            return


@app.task(bind=True, max_retries=None)
def payment_to_billing(self, transaction_id):
    conn = get_redis_connection("default")
    with conn.lock('payment_to_billing-{}'.format(transaction_id)) as lock:
        transaction = Transaction.objects.get(id=transaction_id)

        if transaction.status not in (Transaction.SUCCESS, Transaction.PROCESS_BILLING):
            # Transaction already finished
            logger.info("[{}] Task trying to process already finished {}, close task"
                        .format(self.request.id, transaction))
            return

        # Optimize SQL because too many JOINs
        commission = CounterAgent.objects.filter(billing__clientuser__transaction=transaction.id) \
            .values_list('commission', flat=True)[0]

        # Change status to track errors
        transaction.status = Transaction.PROCESS_BILLING
        transaction.save()

        transaction.timestamp_billing = timezone.now()
        params = {
            'id': transaction.id,
            'account_id': transaction.client_user.billing_userid,
            'amount': transaction.amount * (1. - commission / 100),
            'payment_date': transaction.timestamp_sber.isoformat(),
        }
        enc_params = sign_dict(params, priv_key)
        try:
            resp = requests.post(transaction.client_user.billing.url, json=enc_params)
            # import json
            # resp = FakeResponse()
            # with open("test.txt", "w") as f:
            #     f.write(json.dumps(enc_params))
            #     f.write("\n")
            #     f.write(str(resp.status_code))
            #     f.write("\n")
            #     f.write(str(Path().absolute()))
        except RequestException as e:
            logger.warning("[{}] ({}) Billing request fail: {}, retry after {} secs"
                           .format(self.request.id, transaction, e, RETRY_TIMEOUT))
            raise self.retry(exc=e, countdown=RETRY_TIMEOUT)

        if resp.status_code // 100 != 2:
            logger.warning("[{}] ({}) Billing request return status code {}: {}, retry after {} secs"
                           .format(self.request.id, transaction, resp.status_code, resp.text[:50], RETRY_TIMEOUT))
            raise self.retry(countdown=RETRY_TIMEOUT)
        transaction.status = Transaction.SUCCESS_BILLING
        transaction.save()
        logger.info("[{}] {} was saved in billing system"
                    .format(self.request.id, transaction))
