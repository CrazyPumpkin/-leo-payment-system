import requests
from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect
from rest_framework import status, mixins, permissions
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from users.models import ClientUser
from users.permissions import ActionCombiner
from ..api.serializers import TransactionDefaultSerializer, TransactionCreateSerializer
from ..models import Transaction
from ..tasks import check_transaction


class TransactionViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Transaction.objects.all().order_by("id")
    permission_classes = (ActionCombiner({
        "list": permissions.IsAdminUser,
        "create": permissions.AllowAny,
        "approve_transaction": permissions.AllowAny,
        "metadata": permissions.AllowAny
    }),)

    def filter_queryset(self, queryset):
        order_id = self.request.GET.get("orderId", None)
        if order_id:
            queryset = queryset.filter(paysys_id=order_id)
        return super().filter_queryset(queryset)

    def get_serializer_class(self):
        return {
            "create": TransactionCreateSerializer,
            "approve_transaction": Serializer
        }.get(self.action, TransactionDefaultSerializer)

    def create(self, request, *args, **kwargs):
        """
        Создание *транзакции* для оплаты услуги
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            billing = data["billing"]

            # Create client_user if client_user doesn't exist
            client_user, _created = ClientUser.objects.get_or_create(billing=billing,
                                                                     billing_userid=data["billing_userid"])

            # Create transaction
            tr = Transaction.objects.create(
                service_id=data.get('service_id', None),
                client_user=client_user,
                amount=data['amount'],
                final_url=data['final_url']
            )

        # Set params and do POST request to paysystem API
        SBERBANK = settings.SBERBANK
        params = {
            'userName': SBERBANK['USERNAME'],
            'password': SBERBANK['PASSWORD'],
            'orderNumber': tr.id,
            'amount': data['amount'],
            'language': SBERBANK['LANGUAGE'],
            'returnUrl': reverse('transactions-list', request=request) + 'approve_transaction',
            'currency': SBERBANK['CURRENCY']
        }

        resp = requests.post(SBERBANK['ORDER_REGISTER_URL'], data=params)
        resp_raw = resp.text
        tr.gateway_response = resp_raw
        if resp.status_code // 100 == 2:  # 2** codes
            resp_data = resp.json()
            if resp_data.get('errorCode', None):
                tr.status = Transaction.FAIL
                tr.save()
                response = Response(resp_data['errorMessage'], status=status.HTTP_400_BAD_REQUEST)
            else:
                tr.status = Transaction.CREATED
                tr.paysys_id = resp_data["orderId"]
                task = check_transaction.apply_async((tr.paysys_id,), countdown=SBERBANK['TIMEOUT'])
                tr.task_id = task.id
                tr.save()
                response = HttpResponseRedirect(resp_data['formUrl'])
        else:
            tr.status = Transaction.FAIL
            tr.save()
            response = Response({"data": "payment system error"}, status=resp.status_code)
        return response

    @list_route(methods=["GET"], )
    def approve_transaction(self, request):
        # Run celery task
        order_id = request.GET.get('orderId')
        check_transaction.delay(order_id)
        return HttpResponseRedirect(Transaction.objects.get(paysys_id=order_id).final_url)
