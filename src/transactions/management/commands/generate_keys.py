# -*- coding: utf-8 -*-
import os

import rsa
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Создание ключей шифрования'

    def handle(self, *args, **kwargs):
        for priv, pub, length in (
                (settings.RSA_PAYMENT_PRIV_KEY, settings.RSA_PAYMENT_PUB_KEY, settings.RSA_PAYMENT_KEY_LENGTH),
        ):
            (pubkey, privkey) = rsa.newkeys(length)

            with open(os.path.join(settings.RSA_KEY_HOME, priv), 'wb+') as key_file:
                key_file.write(privkey.save_pkcs1())

            with open(os.path.join(settings.RSA_KEY_HOME, pub), 'wb+') as key_file:
                key_file.write(pubkey.save_pkcs1())
