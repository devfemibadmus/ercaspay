
![Ercaspay](https://sandbox.ercaspay.com/_nuxt/logo.BiwWHVNC.png)

**ERCASPAY** is a Python package that interacts with the [Ercaspay Payment Platform](https://ercaspay.com). It supports various payment methods such as card transactions, USSD, and bank transfers. Along with the Python package, the repo includes a Django app and a Flask app for integrating Ercaspay functionality into web applications.

### For extra support, there is a docstring in every class and function to guide and explain their usage more effectively. Checkout more and test using the [test/test.py](test/test.py) 

## Installation

To get started, install the Ercaspay package via pip:

```bash
pip install ercaspay

```

## Command Line Interface (CLI)

You can use the `ercaspay` command in your terminal to check supported banks and verify if a specific bank is supported.

### List all supported banks:

```bash
ercaspay --bank list

```

### Check if a specific bank is supported:

```bash
ercaspay --bank fcmb

```

## Requirements

The package requires two files to interact with the Ercaspay API:

1.  **ERCASPAY_AUTHORIZATION**: This is required to perform most actions with the Ercaspay API.
2.  **ERCASPAY_PUBLIC_KEY**: This is required for card transactions. **Note:** that when passing the `ERCASPAY_PUBLIC_KEY`, you should **remove** the header and footer before including it in your environment file.

## Setup

### Initialize the Ercaspay Instance

You can initialize the Ercaspay class by either passing an environment file or by directly setting the values in your code.

#### Option 1: Using an Environment File

You can create an `.env` file containing your Ercaspay credentials and configurations. Then, you can initialize the `Ercaspay` instance like this:

```python
from ercaspay import Ercaspay

ercaspay = Ercaspay(env='filename')

```

```bash
# filename content
ERCASPAY_AUTHORIZATION=ECRS-TEST-SKNvIyOB5m62L7GMeP1pJ867074LXvHyeMGyYQT4WF
ERCASPAY_PUBLIC_KEY=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwcyK35rw4X4w9vzb/bcdc1oIClGruVO/2bzlti/U07lWIS4HEZQQwva+rHYniO4yglz0IMJPIT+XteF77303qsAvgYFF4B6OmVtYD7QezLWvVlU0h7oXc9fCz2V+23B6gRUZjmNxE3FMIUhNIb9eqR+rl3wONi1d6qhp6Wsw3ogfcbm9w5RNWgJqFTn+TftxvWmq32TpIKEAIYIHed9SNyKO/BgCKtPedTbKwGCrFQnFFopeKrhJEf5lG5KEu28/50QkmXsjnADW1f4SPhuVqcKt3TDtDkFh5ocxD9fMrSyPV4INBtH18Uf9yDfGwMtBlEj1oTkXVt/evncIjvdXUwIDAQAB
```
#### Option 2: Direct Initialization

Alternatively, you can directly pass the required parameters when initializing the Ercaspay instance:

```python
from ercaspay import Ercaspay

ercaspay = Ercaspay(
    token='ECRS-TEST-SKNvIyOB5m62L7GMeP1pJ867074LXvHyeMGyYQT4WF',
    rsa_key='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwcyK35rw4X4w9vzb/bcdc1oIClGruVO/2bzlti/U07lWIS4HEZQQwva+rHYniO4yglz0IMJPIT+XteF77303qsAvgYFF4B6OmVtYD7QezLWvVlU0h7oXc9fCz2V+23B6gRUZjmNxE3FMIUhNIb9eqR+rl3wONi1d6qhp6Wsw3ogfcbm9w5RNWgJqFTn+TftxvWmq32TpIKEAIYIHed9SNyKO/BgCKtPedTbKwGCrFQnFFopeKrhJEf5lG5KEu28/50QkmXsjnADW1f4SPhuVqcKt3TDtDkFh5ocxD9fMrSyPV4INBtH18Uf9yDfGwMtBlEj1oTkXVt/evncIjvdXUwIDAQAB',
)

```


## Performing Transactions

To perform any transaction (via card, USSD, or bank transfer), you first need to initialize the transaction.

### Example: Common Transaction

```python
# Create the transaction
response = ercaspay.initiate(100000.55, "Test User", "testuser@example.com", "testuser@example.com", redirectUrl='https://example.com')
print(response)

# Get transaction reference
transaction_ref = response['responseBody'].get('transactionReference')

# checking status
response = transaction.status()
print(response)

#  checking details
response = transaction.details()
print(response)

# more in the test/test.py

```
### Example: Card Transaction

```python
# Create the transaction
response = ercaspay.card()
print(response)

# Get response code
response_code = response['responseBody'].get('code')

# if code is C0: transaction successful no auth required

# if code is C2: redirect customer to response['responseBody']['checkoutUrl']

# if code is C1: otp has been sent to customer phone
response = transaction.submit_otp(otp)
print(response)

#  request new otp
response = transaction.resend_otp()
print(response)

# code are determine by the type of card use

```

## Sample Flask and Django Plugin

### Flask Example

You can integrate Ercaspay into your Flask app as follows [test/flask.py](test/flask.py) :

```python
from  flask  import  Flask
from  typing  import  Dict
from  ercaspay.flask  import  ErcaspayPage

app  =  Flask(__name__)
app.secret_key  =  "your-secret-key"

ErcaspayPage(app, "Sponsor Scholarship Contribution", ercaspay_url='/payment')

@app.route("/")
def  hello_world():
    return  "Hello World!"

if  __name__  ==  "__main__":
    app.run(debug=True)

```

### Django Example

In your Django app, you can perform similar operations using views [test/website](test/website):

```python
# Add ercaspay into ur installed app in (settings.py)
INSTALLED_APPS  = [
    #...others
    'ercaspay',
]

# setting conf for ercaspay (settings.py)
ERCASPAY = {
    "ENV": None,
    "TOKEN": None,
    "RSA_KEY": None,
    "CURRENCY": "NGN", # note u can specify currency for each transaction when u integrate
    "ADMIN_SITE": "/",
    "REDIRECT_URL": "/",
    "AUTH_REDIRECT_URL": "auth",
    "PAYMENT_PAGE_NAME": "",
    "PAYMENT_PAGE_DESC": "",
    "NO_PHONE": True
}

# Add path in ur project or app urls, specify any name e.g payment or ercaspay (urls.py)
path('ercaspay/', include('ercaspay.urls')),
```

## Response Handling

Responses from the Ercaspay API are structured into two categories: **failure** and **success**. Below are examples of both types. For more response structures, check the [test/response.txt](test/response.txt) file in this repository.

### Failure Response
Failure responses have a fixed structure and typically include the following keys:
```json
{
  "errorCode": "400",
  "message": "a short msg e.g Bad request",
  "explanation": "a little long explanation that can be displayed in the browser to the user"
}

```

### Success Response

Success responses contain more data, with a dynamic `responseBody` depending on the API call. Examples of success responses:

 -  Example for a successful transaction:
    
    ```json
    {
      "requestSuccessful": true,
      "responseCode": "success",
      "responseMessage": "success",
      "responseBody": {
        "paymentReference": "nigga@example.com",
        "transactionReference": "ERCS|20241217025313|1734400393621",
        "checkoutUrl": "https://sandbox-checkout.ercaspay.com/ERCS|20241217025313|1734400393621"
      }
    }
    
    ```
    
 -  Example for a pending transaction requiring user action:
    
    
    ```json
    {
      "requestSuccessful": true,
      "responseCode": "C1",
      "responseMessage": "success",
      "responseBody": {
        "code": "C1",
        "status": "PENDING",
        "gatewayMessage": "Kindly enter the OTP sent to 234805***1111",
        "supportMessage": "Didn't get the OTP? Dial *723*0# on your phone (MTN, Etisalat, Airtel). For Glo, use *805*0#.",
        "transactionReference": "ERCS|20241217025313|1734400393621",
        "paymentReference": "nigga@example.com",
        "gatewayReference": "oCKuDTqT2l",
        "amount": 100050,
        "callbackUrl": "https://nigga.com"
      }
    }
    
    ```
 -  Some Others

```python
checkout
{'requestSuccessful': True, 'responseCode': 'success', 'responseMessage': 'success', 'responseBody': {'paymentReference': 'nigga@example.com', 'transactionReference': 'ERCS|20241217025313|1734400393621', 'checkoutUrl': 'https://sandbox-checkout.ercaspay.com/ERCS|20241217025313|1734400393621'}}

card C1
{'requestSuccessful': True, 'responseCode': 'C1', 'responseMessage': 'success', 'responseBody': {'code': 'C1', 'status': 'PENDING', 'gatewayMessage': 'Kindly enter the OTP sent to 234805***1111', 'supportMessage': "Didn't get the OTP? Dial *723*0# on your phone (MTN,Etisalat,Airtel) Glo,use *805*0#.", 'transactionReference': 'ERCS|20241217025313|1734400393621', 'paymentReference': 'nigga@example.com', 'gatewayReference': 'oCKuDTqT2l', 'amount': 100050, 'callbackUrl': 'https://nigga.com'}}

card C2
{'requestSuccessful': True, 'responseCode': 'success', 'responseMessage': 'success', 'responseBody': {'paymentReference': 'nigga@example.com', 'transactionReference': 'ERCS|20241217050928|1734408568497', 'checkoutUrl': 'https://sandbox-checkout.ercaspay.com/ERCS|20241217050928|1734408568497'}}

error
{'errorCode': '400', 'message': 'Bad Request', 'explanation': 'wrong amount provided'} 

submit otp
{'requestSuccessful': True, 'responseCode': 'success', 'responseMessage': 'success', 'responseBody': {'status': 'SUCCESS', 'gatewayMessage': 'OTP Authorization Successful', 'transactionReference': 'ERCS|20241217025313|1734400393621', 'paymentReference': 'nigga@example.com', 'amount': 100000.55, 'callbackUrl': 'https://nigga.com'}}

check transaction status
{'requestSuccessful': True, 'responseCode': 'success', 'responseMessage': 'success', 'responseBody': {'paymentReference': 'nigga@example.com', 'amount': 100000.55, 'status': 'PAID', 'description': None, 'callbackUrl': 'https://nigga.com?reference=nigga@example.com&status=PAID&transRef=ERCS|20241217025313|1734400393621'}}

cancel transaction
{'requestSuccessful': True, 'responseCode': 'success', 'responseMessage': 'success', 'responseBody': {'callback_url': 'https://nigga.com?reference=nigga@example.com&status=CANCELLED'}}

{'requestSuccessful': True, 'responseCode': 'success', 'responseMessage': 'success', 'responseBody': {'paymentReference': 'nigga@example.com', 'amount': 122200.55, 'status': 'CANCELLED', 'description': None, 'callbackUrl': 'https://nigga.com?reference=nigga@example.com&status=CANCELLED&transRef=ERCS|20241216075712|1734332232972'}}

check transaction details
{'amount': '111111', 'paymentReference': '23784c3611e74debad224b23cc76b80f_20241216205542', 'paymentMethods': 'card, bank-transfer, qrcode, ussd', 'customerName': 'ttttt testing', 'currency': 'NGN', 'customerEmail': 'thegudbadguys@gmail.com', 'customerPhoneNumber': '09082838383', 'redirectUrl': 'http://127.0.0.1:8000/ercaspay/auth', 'description': None, 'metadata': None, 'feeBearer': None}
{'errorCode': '400', 'message': 'Bad Request', 'explanation': 'This payment has already been completed'}

for more test use the test.py file

```

## License  
This project is managed under a license by [Ercaspay](https://ercaspay.com).  

## Contribution  
Contributions are welcome! You can open an issue in this repository to report bugs, suggest features, or provide feedback.  


![Ercaspay Workflow](https://sandbox-checkout.ercaspay.com/apple-touch-icon.png)