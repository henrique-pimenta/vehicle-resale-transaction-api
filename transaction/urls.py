from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "api/transactions/",
        include(("transaction.apps.transaction.urls", "vehicle"), namespace="transaction.apps.transaction"),
    ),
]
