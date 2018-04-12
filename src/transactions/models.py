import json

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from users.models import ClientUser


class Transaction(models.Model):
    INITIAL, CREATED, SUCCESS, FAIL, PROCESS_BILLING, SUCCESS_BILLING = range(6)

    STATUS_CHOICES = (
        (INITIAL, _('Новая')),
        (CREATED, _('Создана')),
        (SUCCESS, _('Успешна')),
        (FAIL, _('Ошибка/Возврат')),
        (PROCESS_BILLING, _('Передача информации биллингу')),
        (SUCCESS_BILLING, _('Успешна (инф. передана биллингу)')),
    )

    STATUS_SBER_CHOICES = (
        (100, "-----"),
        (0, "Заказ зарегистрирован, но не оплачен"),
        (1, "Предавторизованная сумма захолдирована (для двухстадийных платежей)"),
        (2, "Проведена полная авторизация суммы заказа"),
        (3, "Авторизация отменена"),
        (4, "По транзакции была проведена операция возврата"),
        (5, "Инициирована авторизация через ACS банка-эмитента"),
        (6, "Авторизация отклонена"),
    )

    STATUS_SBER_OK = (2,)
    STATUS_SBER_PENDING = (0, 1, 5)
    STATUS_SBER_FAIL = (3, 4, 6)

    paysys_id = models.CharField(verbose_name=_('Номер заказа в платежной системе'), max_length=64, blank=True)
    service_id = models.PositiveIntegerField(verbose_name=_('ID услуги'), null=True, blank=True)

    client_user = models.ForeignKey(ClientUser, verbose_name=_('Плательщик'), on_delete=models.CASCADE)

    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=INITIAL, verbose_name=_('Статус'))
    status_sber = models.PositiveSmallIntegerField(choices=STATUS_SBER_CHOICES,
                                                   verbose_name=_('Статус платежной системы'), default=100)
    amount = models.PositiveIntegerField(verbose_name=_('Сумма (коп.)'))
    final_url = models.URLField(verbose_name=_('URL для редиректа после потверждения оплаты'))
    gateway_response = models.CharField(verbose_name=_('Данные ответа платежного шлюза'), blank=True, max_length=1024)
    gateway_status = models.CharField(verbose_name=_('Данные статуса платежного шлюза'), blank=True, max_length=1024)

    sber_client_ip = models.CharField(verbose_name=_("IP адрес покупателя"), max_length=30, blank=True)
    sber_client_cardholder_name = models.CharField(verbose_name=_("Имя держателя карты"), max_length=255, blank=True)

    timestamp = models.DateTimeField(verbose_name=_('Дата создания'), auto_now_add=True)
    timestamp_sber = models.DateTimeField(verbose_name=_('Дата оплаты'), null=True, blank=True)
    timestamp_billing = models.DateTimeField(verbose_name=_('Дата проведения'), null=True, blank=True)

    task_id = models.CharField(verbose_name=_('task_id (20 мин.)'), max_length=255, blank=True)

    @property
    def status_ok(self):
        return self.status == self.SUCCESS or self.status == self.CREATED and self.status_sber in self.STATUS_SBER_OK

    @property
    def status_pending(self):
        return self.status == self.INITIAL or self.status == self.CREATED and self.status_sber in self.STATUS_SBER_PENDING

    @property
    def status_fail(self):
        return self.status == self.FAIL or self.status_sber in self.STATUS_SBER_FAIL

    @property
    def id_(self):
        # Формы ломаются при попытке добавить в них id, так что испоьзуем этот костыль
        return self.id

    id_.fget.short_description = _("ID")

    @property
    def amount_verbose(self):
        return "{:.2f}".format(self.amount / 100) if self.amount else None

    amount_verbose.fget.short_description = _("Сумма (руб.)")

    @cached_property
    def gateway_status_json(self):
        if self.gateway_status:
            try:
                data = json.loads(self.gateway_status)
            except json.JSONDecodeError:
                data = None
            return data if isinstance(data, dict) else {}
        return {}

    def gateway_status_arg(self, arg: str):
        # Sberbank return some(!) keys capitalized and it's not documented
        return self.gateway_status_json.get(arg, self.gateway_status_json.get(arg.capitalize(), ""))


    @property
    def sber_client_pan(self):
        return self.gateway_status_arg("pan")

    sber_client_pan.fget.short_description = _("Номер карты")

    @property
    def sber_client_expiration(self):
        return self.gateway_status_arg("expiration")

    sber_client_expiration.fget.short_description = _("Срок истечение действия карты")


    class Meta:
        verbose_name = _('Транзакция')
        verbose_name_plural = _('Транзакции')

    def __str__(self):
        return "Transaction#" + str(self.id)

    def save(self, *args, **kwargs):
        if self.gateway_status_json:
            self.sber_client_ip = self.gateway_status_arg("ip")
            self.sber_client_cardholder_name = self.gateway_status_arg("cardholderName").capitalize()
        super(Transaction, self).save(*args, **kwargs)


# Checking groups of sber statuses
assert set(Transaction.STATUS_SBER_OK) | set(Transaction.STATUS_SBER_PENDING) | set(Transaction.STATUS_SBER_FAIL) \
       == set(range(7))
assert len(Transaction.STATUS_SBER_OK + Transaction.STATUS_SBER_PENDING + Transaction.STATUS_SBER_FAIL) == 7
