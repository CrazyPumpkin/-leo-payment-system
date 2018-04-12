from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Sum, Q
from django.utils.translation import ugettext_lazy as _

from transactions.models import Transaction
from .models import StaffUser, ClientUser


@admin.register(StaffUser)
class StaffUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email',)
    list_filter = ('is_staff', 'is_superuser', 'groups')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(ClientUser)
class ClientUserAdmin(ModelAdmin):
    list_display = ('billing', 'billing_userid', 'incoming')
    list_filter = ('billing',)

    def get_queryset(self, request):
        qs = super(ModelAdmin, self).get_queryset(request)
        return qs.annotate(incoming=Sum(
            'transaction__amount',
            filter=Q(transaction__status=Transaction.SUCCESS_BILLING)
        ))

    def incoming(self, client):
        return "{:.2f}".format(client.incoming / 100) if client.incoming else '-'

    incoming.admin_order_field = 'incoming'
    incoming.short_description = _("Сумма (руб.)")
