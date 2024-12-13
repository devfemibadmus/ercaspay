import requests, os
from ercaspay import load_env_vars

load_env_vars('.env')

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ.get('Authorization')}"
}
json = {
    "amount": 10000,
    "paymentReference": "johndoe@gmail.com",
    "paymentMethods": "bank-transfer",
    "customerName": "John Doe",
    "customerEmail": "johndoe@gmail.com",
    "customerPhoneNumber": "09061626364",
    "redirectUrl": "https://omolabakeventures.com",
    "description": "The description for this payment goes here",
    "currency": "NGN",
    "feeBearer": "customer",
    "metadata": {
        "firstname": "Ola",
        "lastname": "Benson",
        "email": "iie@mail.com"
    }
}
response = requests.post('https://api.merchant.staging.ercaspay.com/api/v1/payment/initiate', headers=headers, json=json)
print(response.json())