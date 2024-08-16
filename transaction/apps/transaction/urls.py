from django.urls import path, include
from rest_framework.routers import DefaultRouter

from inventory.apps.inventory.views import TransactionViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
