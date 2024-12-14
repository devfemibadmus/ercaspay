from ercaspay import Ercaspay

ercaspay = Ercaspay()
response = ercaspay.initiate_Transaction(100.55, "test", "nigga@example.com", "nigga@example.com", redirectUrl='https://nigga.com')
print(response)

transaction_ref = response['responseBody'].get('transactionReference')

response = ercaspay.cancel_transaction(transaction_ref)
print(response)
response = ercaspay.details_transaction(transaction_ref)
print(response)
response = ercaspay.status_transaction('transaction_ref')
print(response)
"""
response = ercaspay.details_transaction(transaction_ref)
print(response)
response = ercaspay.status_transaction(transaction_ref)
print(response)
"""