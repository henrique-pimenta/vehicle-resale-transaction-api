import json
import uuid

import boto3
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from transaction.apps.transaction.gateways import generate_payment_link
from transaction.apps.transaction.models import PaymentStatus, ReservationStatus, Transaction, WithdrawalStatus
from transaction.apps.transaction.serializers import TransactionSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='confirm-payment')
    def confirm_payment(self, request, pk=None):
        transaction = self.get_object()
        if transaction.status != PaymentStatus.PENDINDG.value:
            return Response(status=status.HTTP_404_NOT_FOUND)

        transaction.payment_status = PaymentStatus.PAID.value
        transaction.save()

        self.publish_event('payment_confirmed', dict(TransactionSerializer(transaction).data))

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='payment-failed')
    def payment_failed(self, request, pk=None):
        transaction = self.get_object()
        if transaction.status != PaymentStatus.PENDINDG.value:
            return Response(status=status.HTTP_404_NOT_FOUND)

        transaction.payment_status = PaymentStatus.FAILED.value
        transaction.reservation_status = ReservationStatus.CANCELED.value
        transaction.save()

        event_data = dict(TransactionSerializer(transaction).data)
        self.publish_event('payment_failed', event_data)

        return Response(status=status.HTTP_200_OK)

    def publish_event(self, event_type: str, detail: dict):
        event_bridge = boto3.client('events')
        event_bridge.put_events(
            Entries=[
                {
                    'Source': 'transaction_service',
                    'DetailType': event_type,
                    'Detail': json.dumps(),
                    'EventBusName': 'vehicle_resale_event_bus'
                }
            ]
        )

    @action(detail=False, methods=['post'], url_path='event-handler')
    def event_handler(self, request):
        if request.method == 'POST':
            event_data = request.data

            event_type = event_data.get("detail-type")
            if not event_type:
                return Response({'error': 'detail-type is required'}, status=status.HTTP_400_BAD_REQUEST)

            event_detail = event_data.get("detail")
            if not event_detail:
                return Response({'error': 'detail is required'}, status=status.HTTP_400_BAD_REQUEST)

            vehicle_id = event_detail.get("vehicle_id")
            if not vehicle_id:
                return Response({'error': 'vehicle_id is required'}, status=status.HTTP_400_BAD_REQUEST)

            user_id = event_detail.get("user_id")
            if not user_id:
                return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

            if event_type == 'vehicle_selected':
                transactions = Transaction.objects.filter(vehicle_id=vehicle_id, reservation_status=ReservationStatus.RESERVED.value)
                if transactions.exists():
                    self.publish_event('reservation_failed', dict(TransactionSerializer(transactions.first()).data))
                    return Response({'error': 'reservation failed'}, status=status.HTTP_404_NOT_FOUND)

                new_transaction = Transaction(
                    id=str(uuid.uuid4()),
                    vehicle_id=vehicle_id,
                    price_cents=event_detail.get('price_cents'),
                    user_id=user_id,
                    reservation_status=ReservationStatus.RESERVED.value,
                    payment_status=PaymentStatus.PENDINDG.value,
                    withdrawal_status=WithdrawalStatus.PENDINDG.value,
                )
                new_transaction.save()

                try:
                    payment_link = generate_payment_link(new_transaction.id, new_transaction.price_cents)
                    payment_generated_event = {
                        user_id: new_transaction.user_id,
                        payment_link: payment_link,
                    }
                    self.publish_event('payment_generated', payment_generated_event)
                except:
                    new_transaction.reservation_status = ReservationStatus.CANCELED.value
                    new_transaction.save()
                    self.publish_event('reservation_failed', dict(TransactionSerializer(new_transaction).data))

            elif event_type == 'withdrawal_confirmed':
                transactions = Transaction.objects.filter(vehicle_id=vehicle_id, reservation_status=ReservationStatus.RESERVED.value)
                if not transactions.exists():
                    return Response(status=status.HTTP_404_NOT_FOUND)

                transaction = transactions.first()
                transaction.withdrawal_status = WithdrawalStatus.WITHDRAWN.value
                transaction.save()

            elif event_type == 'inventory_update_failed':
                transactions = Transaction.objects.filter(vehicle_id=vehicle_id, reservation_status=ReservationStatus.RESERVED.value)
                if transactions.exists():
                    for transaction in transactions:
                        transaction.reservation_status = ReservationStatus.CANCELED.value
                        transaction.save()

            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)
