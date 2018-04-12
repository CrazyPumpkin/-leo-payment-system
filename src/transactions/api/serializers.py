import json

from rest_framework import serializers

from billing.models import Billing
from transactions.models import Transaction
from users.api.serializers import ClientUserSerializer


class NaturalKey(serializers.RelatedField):
    def __init__(self, natural_key, **kwargs):
        super().__init__(**kwargs)
        self.natural_key = natural_key

    def to_representation(self, value):
        return getattr(value, self.natural_key)

    def to_internal_value(self, data):
        return self.queryset.get(**{self.natural_key: data})


class TransactionCreateSerializer(serializers.Serializer):
    service_id = serializers.IntegerField(allow_null=True, required=False)
    billing = NaturalKey(allow_null=False, natural_key='system_name', queryset=Billing.objects.all(),
                         source="client_user.billing")
    billing_userid = serializers.IntegerField(allow_null=False)
    amount = serializers.IntegerField(allow_null=False)
    final_url = serializers.URLField(allow_null=False)

    def validate(self, attrs):
        data = super(TransactionCreateSerializer, self).validate(attrs)
        data.update({"billing": attrs.get("client_user", {}).get("billing", None)})
        return data


class TransactionDefaultSerializer(serializers.ModelSerializer):
    client_user = ClientUserSerializer()
    billing = NaturalKey(allow_null=False, natural_key='system_name', queryset=Billing.objects.all(),
                         source="client_user.billing")
    gateway_response = serializers.SerializerMethodField()
    gateway_status = serializers.SerializerMethodField()

    def get_gateway_response(self, obj):
        return json.loads(obj.gateway_response) if obj.gateway_response else None

    def get_gateway_status(self, obj):
        return json.loads(obj.gateway_status) if obj.gateway_status else None

    class Meta:
        model = Transaction
        fields = '__all__'
