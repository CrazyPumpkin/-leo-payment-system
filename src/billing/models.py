from django.db import models
from django.utils.translation import ugettext_lazy as _


class CounterAgent(models.Model):
    name = models.CharField(verbose_name=_('Название'), max_length=250)
    commission = models.PositiveSmallIntegerField(verbose_name=_('Комиссия (%)'),
                                                  help_text=_('проценты (0 - 100%)'), default=0)

    class Meta:
        verbose_name = _('Контрагент')
        verbose_name_plural = _('Контрагенты')

    def __str__(self):
        return self.name


class Billing(models.Model):
    name = models.CharField(verbose_name=_('Название'), max_length=250)
    system_name = models.SlugField(verbose_name=_('Системное название'), max_length=250, unique=True)
    counter_agent = models.ForeignKey(CounterAgent, verbose_name=_('Контрагент'), on_delete=models.CASCADE)
    url = models.URLField(verbose_name=_('URL биллинга'))

    class Meta:
        verbose_name = _('Биллинг')
        verbose_name_plural = _('Биллинги')

    def __str__(self):
        return self.name
