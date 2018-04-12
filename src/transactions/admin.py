from collections import OrderedDict

from admin_view_permission.admin import AdminViewPermissionModelAdmin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django_admin_listfilter_dropdown.filters import ChoiceDropdownFilter, RelatedDropdownFilter
from import_export import fields
from import_export.admin import ExportActionModelAdmin

from etc.admin_filters import DateRangeFilter
from etc.resource_utils import CustomModelResource
from .models import Transaction

TRANSACTION_ADMIN_FIELDS = (
    "id_", "amount", "status", "status_sber", "client_user",
    "paysys_id", "sber_client_ip", "sber_client_pan", "sber_client_expiration", "sber_client_cardholder_name",
    "timestamp", "timestamp_sber", "timestamp_billing"
)


class TransactionResource(CustomModelResource):
    id_ = fields.Field(attribute='id_')
    sber_client_ip = fields.Field(attribute='sber_client_ip')
    sber_client_pan = fields.Field(attribute='sber_client_pan')
    sber_client_expiration = fields.Field(attribute='sber_client_expiration')
    sber_client_cardholder_name = fields.Field(attribute='sber_client_cardholder_name')

    class Meta:
        model = Transaction
        fields = TRANSACTION_ADMIN_FIELDS
        export_order = TRANSACTION_ADMIN_FIELDS
        choice_fields = ('status', 'status_sber')
        str_fields = ('client_user',)
        summary_filter = lambda qs: qs.filter(status=Transaction.SUCCESS_BILLING)
        summary_fields = ('amount',)


@admin.register(Transaction)
class TransactionAdmin(ExportActionModelAdmin, AdminViewPermissionModelAdmin):
    fieldsets = (
        (
            None,
            {"fields": (
                "id_",
                "amount_verbose",
                "status"
            )}
        ), (
            _("Системная информация"),
            {"fields": (
                "service_id",
                "client_user",
                "final_url"
            )}
        ), (
            _("Временные метки"),
            {"fields": (
                "timestamp",
                "timestamp_sber",
                "timestamp_billing"
            )}
        ), (
            _("Данные платежной системы"),
            {"fields": (
                "paysys_id",
                "status_sber",
                "sber_client_ip",
                "sber_client_pan",
                "sber_client_expiration",
                "sber_client_cardholder_name",
            )}
        )
    )
    readonly_fields = ("id_", "timestamp", "amount_verbose", "sber_client_pan", "sber_client_expiration")
    list_display = TRANSACTION_ADMIN_FIELDS
    date_hierarchy = "timestamp"
    list_filter = (
        ("timestamp_sber", DateRangeFilter),
        "status",
        ("status_sber", ChoiceDropdownFilter),
        ("client_user__billing", RelatedDropdownFilter),
        ("client_user__billing__counter_agent", RelatedDropdownFilter),
    )
    search_fields = ("id", "sber_client_ip", "sber_client_cardholder_name", "sber_client_pan")
    list_per_page = 100

    resource_class = TransactionResource
    change_list_template = 'admin/import_export/change_list_export.html'

    def sber_client_expiration(self, transaction):
        exp = transaction.sber_client_expiration
        return "/".join((exp[:4], exp[4:])) if exp else ""

    sber_client_expiration.short_description = Transaction.sber_client_expiration.fget.short_description
    sber_client_expiration.admin_order_field = 'sber_client_expiration'

    def get_actions(self, request):
        actions = super(TransactionAdmin, self).get_actions(request)
        if not actions:
            return OrderedDict([[
                "export_admin_action",
                (
                    ExportActionModelAdmin.export_admin_action,
                    "export_admin_action",
                    ExportActionModelAdmin.export_admin_action.short_description
                )
            ]])
        return actions
