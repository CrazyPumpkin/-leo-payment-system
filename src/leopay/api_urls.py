from django.urls import include, path


urlpatterns = [
    path('transactions/', include('transactions.api.urls')),
    path('users/', include('users.api.urls')),
]
