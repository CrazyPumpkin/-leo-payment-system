from rest_framework import viewsets

from users.api.serializers import ClientUserSerializer
from users.models import ClientUser


class ClientUserViewSet(viewsets.ModelViewSet):
    queryset = ClientUser.objects.all()
    serializer_class = ClientUserSerializer
