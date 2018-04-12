from rest_framework import serializers

from users.models import ClientUser


class ClientUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientUser
        fields = '__all__'
