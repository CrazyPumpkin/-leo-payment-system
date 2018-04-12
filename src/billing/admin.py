from django.contrib import admin

from billing.models import CounterAgent, Billing


class CounterAgentAdmin(admin.ModelAdmin):
    pass


class BillingAdmin(admin.ModelAdmin):
    pass


admin.site.register(CounterAgent, CounterAgentAdmin)
admin.site.register(Billing, BillingAdmin)
