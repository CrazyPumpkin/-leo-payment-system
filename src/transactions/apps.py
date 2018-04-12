from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TransactionsConfig(AppConfig):
    name = 'transactions'
    verbose_name = _('Транзакции')
