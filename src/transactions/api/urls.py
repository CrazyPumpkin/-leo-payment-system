from rest_framework import routers

from transactions.api.views import TransactionViewSet

router = routers.DefaultRouter()
router.register('', TransactionViewSet, base_name="transactions")

urlpatterns = [] + router.urls
