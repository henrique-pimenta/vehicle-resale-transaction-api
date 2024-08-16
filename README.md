# vehicle-resale-transaction-api
Repository to keep the code of an Transaction Service API. This service is dedined to be integrated with Amazon EventBridge, API Gateway, and an external Payment Gateway.

# Endpoints:

    GET /api/transactions/transactions/ (List all transactions)
    POST /api/transactions/transactions/<id>/confirm-payment/ (Payment Gateway confirms a successful payment)
    POST /api/transactions/transactions/<id>/payment-failed/ (Payment Gateway informs of a failed or unpaid payment)
    POST /api/transactions/transactions/event-handler/ (Handle events)
