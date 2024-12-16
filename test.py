from ercaspay import Ercaspay


transaction = Ercaspay()

ref2 = 'ERCS|20241214192716|1734200836126'
response = transaction.initiate(122200.55, "test", "nigga@example.com", "nigga@example.com", redirectUrl='https://nigga.com')
print(response)
response = transaction.status()
print(response)
response = transaction.details()
print(response)

card = {
        'cvv' : '100',
        'pin' : '1234',
        'expiryDate' : '0139',
        'pan' : '5123450000000008'
    }
browserDetails = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "3DSecureChallengeWindowSize": "FULL_SCREEN",
    "acceptHeaders": "application/json",
    "colorDepth": 24,
    "javaEnabled": True,
    "language": "en-US",
    "screenHeight": 473,
    "screenWidth": 1600,
    "timeZone": 273
}
ipAddress = "41.242.77.212"
response = transaction.card(card, browserDetails, ipAddress)
print(response)

"""
response = transaction.initiate(100.55, "test", "nigga@example.com", "nigga@example.com", redirectUrl='https://nigga.com')
print(response)
transaction_ref = response['responseBody'].get('transactionReference')

response = transaction.bank_list()
print(response)
response = transaction.bank(transaction_ref)
print(response)

response = transaction.details('ERCS|20241214192716|1734200836126')
print(response)
response = transaction.status('ERCS|20241214192716|1734200836126')
print(response)

response = transaction.ussd('ERCS|20241214185857|1734199137582', 'fcmmb')
print(response)
response = transaction.cancel(transaction_ref)
print(response)
response = transaction.details(transaction_ref)
print(response)
response = transaction.status('transaction_ref')
print(response)
response = transaction.details(transaction_ref)
print(response)
response = transaction.status(transaction_ref)
print(response)
"""