from enum import Enum

from django.db import models


class ReservationStatus(Enum):
    CANCELED = "canceled"
    RESERVED = "reserved"


class PaymentStatus(Enum):
    PENDINDG = "pending"
    PAID = "paid"
    FAILED = "failed"


class WithdrawalStatus(Enum):
    PENDINDG = "pending"
    WITHDRAWN = "withdrawn"
    FAILED = "failed"


class Transaction(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    vehicle_id = models.CharField(max_length=36)
    price_cents = models.IntegerField()
    user_id = models.CharField(max_length=100)
    reservation_status = models.CharField(
        max_length=9,
        choices=[(status.value, status.value) for status in ReservationStatus],
    )
    payment_status = models.CharField(
        max_length=9,
        choices=[(status.value, status.value) for status in PaymentStatus],
    )
    withdrawal_status = models.CharField(
        max_length=9,
        choices=[(status.value, status.value) for status in WithdrawalStatus],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
