from collections import OrderedDict

import rangefilter.filter
from django.contrib.admin.widgets import AdminDateWidget
from django.forms import DateField
from django.utils.translation import ugettext_lazy as _


class DateRangeFilter(rangefilter.filter.DateRangeFilter):
    # Just changed two placeholders
    def _get_form_fields(self):
        return OrderedDict((
            (self.lookup_kwarg_gte, DateField(
                label='',
                widget=AdminDateWidget(attrs={'placeholder': _('От')}),
                localize=True,
                required=False
            )),
            (self.lookup_kwarg_lte, DateField(
                label='',
                widget=AdminDateWidget(attrs={'placeholder': _('До')}),
                localize=True,
                required=False
            )),
        ))
