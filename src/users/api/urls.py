from rest_framework import routers

router = routers.DefaultRouter()
# router.register('', ClientUserViewSet)


urlpatterns = [] + router.urls
