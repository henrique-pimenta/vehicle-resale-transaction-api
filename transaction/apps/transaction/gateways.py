from decouple import config
import requests


def generate_payment_link(transaction_id: str, amount: int):
    # url = config('PAYMENT_GATEWAY_URL')
    # headers = {
    #   "Authorization": f'Bearer {config("PAYMENT_GATEWAY_URL")}'
    # }
    # data = {
    #   "transaction_id": transaction_id,
    #   "amount": amount
    # }
    # response = requests.post(url, headers=headers, json=data)
    # response.raise_for_status()
    # payment_link = response.json(){"payment_link"}
    # return payment_link
    return 'mock_payment_link'
