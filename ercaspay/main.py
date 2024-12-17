from .utility import *

class Ercaspay:
    """
    ![Ercaspay Workflow](https://sandbox-checkout.ercaspay.com/apple-touch-icon.png)

    | Argument          | Type   | Default  | Description                                                                                         |
    |-------------------|--------|----------|-----------------------------------------------------------------------------------------------------|
    | rsa_key    | str    | None     | The RSA public key as a string or file path. If not provided, it attempts to load from environment variables. |
    | env               | str    | ".env"   | The environment file to use for configuration. Defaults to '.env'.                                 |
    | token             | str    | None     | The authorization token. If not provided, it will be retrieved based on the environment.           |

    Learn more: https://github.com/devfemibadmus/ercaspay
    """
    def __init__(self, rsa_key: str = None, env: str = None, token: str = None):
        self.token = token or get_token(env)
        self.rsa_key = rsa_key
        self.gatewayReference = None
        self.transaction_ref = None
        self.headers = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}

    def initiate(self, amount: float, customerName: str,
        customerEmail: str, paymentReference: str, paymentMethods: str = None,
        customerPhoneNumber: str = None, redirectUrl: str = None,
        description: str = None, metadata: str = None,
        feeBearer: str = None, currency: str = "NGN") -> dict:
        """
        Initiates a payment transaction on the Ercaspay platform.

        | Argument            | Type   | Default  | Description                                                                 |
        |---------------------|--------|----------|-----------------------------------------------------------------------------|
        | amount              | float  | N/A      | Transaction amount in the specified currency.                               |
        | customerName        | str    | N/A      | Full name of the customer initiating the transaction.                       |
        | customerEmail       | str    | N/A      | Email address of the customer.                                              |
        | paymentReference    | str    | N/A      | A unique reference for this payment.                                        |
        | paymentMethods      | str    | None     | Allowed payment methods (e.g., 'card', 'bank-transfer').                    |
        | customerPhoneNumber | str    | None     | Customer's phone number (if provided).                                      |
        | redirectUrl         | str    | None     | URL to redirect the customer after payment.                                 |
        | description         | str    | None     | Additional description for the transaction.                                 |
        | metadata            | str    | None     | Any additional metadata of customer (e.g., 'firstname', 'lastname').        |
        | feeBearer           | str    | None     | Entity bearing the transaction fees (e.g., customer or merchant).          |
        | currency            | str    | "NGN"    | Transaction currency (default is "NGN").                                    |

        Returns:
            dict: Response from the Ercaspay API after initiating the transaction.
        """
        currency_code = formatCurrency(currency)
        payload = {
            "amount": amount,
            "paymentReference": paymentReference,
            "paymentMethods": formatPaymentMethods(paymentMethods),
            "customerName": customerName,
            "currency": currency_code,
            "customerEmail": customerEmail,
            "customerPhoneNumber": customerPhoneNumber,
            "redirectUrl": redirectUrl,
            "description": description,
            "metadata": metadata,
            "feeBearer": feeBearer,
        }
        transaction = send_payment_request(initiateUrl, payload=payload, headers=self.headers)
        self.transaction_ref = transaction.get('responseBody', {}).get('transactionReference')
        return transaction

    def cancel(self, transaction_ref: str = None) -> dict:
        """
        Cancels an ongoing or scheduled transaction on Ercaspay.

        Args:
            transaction_ref (str): Unique reference for the transaction to cancel. Defaults to the reference used in the initiated transaction (self).

        Returns:
            dict: Response from the Ercaspay API after attempting to cancel the transaction.
        """
        transaction_ref = get_transaction_ref(transaction_ref, self.transaction_ref)
        return send_payment_request(f"{cancelUrl}/{transaction_ref}", {}, self.headers)

    def verify(self, transaction_ref: str = None) -> dict:
        """
        Verifies the status of a transaction using its reference.

        Args:
            transaction_ref (str): Unique reference for the transaction to verify. Defaults to the reference used in the initiated transaction (self).

        Returns:
            dict: Response containing transaction verification details from the API.
        """
        transaction_ref = get_transaction_ref(transaction_ref, self.transaction_ref)
        return send_payment_request(f"{verifyUrl}/{transaction_ref}", {}, self.headers)

    def details(self, transaction_ref: str = None) -> dict:
        """
        Retrieves detailed information about a specific transaction.

        Args:
            transaction_ref (str): Unique reference for the transaction to retrieve details for. Defaults to the reference used in the initiated transaction (self).

        Returns:
            dict: Detailed transaction information from the API.
        """
        transaction_ref = get_transaction_ref(transaction_ref, self.transaction_ref)
        return send_payment_request(f"{detailsUrl}/{transaction_ref}", {}, self.headers)

    def status(self, transaction_ref: str = None, reference: str = None, payment_method: str = None) -> dict:
        """
        Checks the payment status of a specific transaction.

        Args:
            transaction_ref (str): Unique reference for the transaction. Defaults to the reference used in the initiated transaction (self).
            reference (str): Additional reference for specific payment status queries.
            payment_method (str): Payment method used (e.g., 'bank-transfer', 'card'). Defaults to 'bank-transfer'.

        Returns:
            dict: Response containing the current status of the transaction.
        """
        transaction_ref = get_transaction_ref(transaction_ref, self.transaction_ref)
        payment_method = payment_method.strip().lower() if payment_method else "bank-transfer"
        if payment_method not in valid_payment_methods:
            payment_method = "bank-transfer"
        payload = {
            "payment_method": payment_method,
            "reference": reference,
        }
        return send_payment_request(f"{statusUrl}/{transaction_ref}", payload, self.headers)

    def ussd(self, bank_name: str, transaction_ref: str = None, amount: float=None) -> dict:
        """
        Generates a USSD code for a transaction, allowing customers to complete payment via USSD.

        Args:
            bank_name (str): Name of the bank for the USSD payment.
            transaction_ref (str): Unique reference for the transaction. Defaults to the reference used in the initiated transaction (self).
            amount (optional[float]): Transaction amount (optional).

        Returns:
            dict: Response containing the USSD code and related details.
        """
        # bank_name = bank_name.strip().lower()
        # if bank_name not in valid_bank_names:
        #     return handle_error_msg(422, {'errorMessage': 'The selected bank name is invalid.'})
        transaction_ref = get_transaction_ref(transaction_ref, self.transaction_ref)
        if amount is None:
            transaction = self.details(transaction_ref)
            amount = transaction.get('responseBody', {}).get('amount')
            if not amount:
                return transaction
        payload = {
            "amount": amount,
            "bank_name": bank_name,
        }
        return send_payment_request(f"{ussdUrl}/request-ussd-code/{transaction_ref}", payload, self.headers)

    def supported_bank_list(self) -> dict:
        """
        Get all the supported banks for USSD transfer

        Returns:
            dict: Response containing the USSD code and related details.
        """
        return supported_banks()
    
    def support_bank(self, bank_name: str) -> bool:
        """
        Get all the supported banks for USSD transfer

        Returns:
            dict: Response containing the USSD code and related details.
        """
        return support_bank(bank_name)

    def bank(self, transaction_ref: str = None) -> dict:
        """
        Generates a bank detail for a transaction, allowing customers to complete payment via transfer.

        Args:
            transaction_ref (str): Unique reference for the transaction. Defaults to the reference used in the initiated transaction (self).

        Returns:
            dict: Detailed transaction information from the API.
        """
        transaction_ref = get_transaction_ref(transaction_ref, self.transaction_ref)
        return send_payment_request(f"{bankUrl}/{transaction_ref}", {}, self.headers)

    def card(self, cardDetails: dict, browserDetails: dict, ipAddress: str = None, transaction_ref: str = None) -> dict:
        """
        Processes a card transaction using the provided transaction reference, browser details, optional IP address, 
        and card details.

        Args:
            - cardDetails Example:
            
            ```python
            # A dictionary containing card-specific details. Remove the slash e.g 12/23 to 1223 in expire date
            cardDetails = {'cardType': 'Visa', 'pan': 4111111111111111, 'expiryDate': 1223, 'pin': 1234, 'cvv': 123, 'otp': 987654, 'status': active}
            ```
            - browserDetails Example:
            
            ```python
            # A dictionary containing browser-specific details
            browserDetails = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...' , '3DSecureChallengeWindowSize': 'FULL_SCREEN', 'colorDepth': 24,'javaEnabled': True, 'language': 'en-NG', 'screenHeight': 1080, 'screenWidth': 1920, 'timeZone': 'UTC+1:00'}
            ```

            - ipAddress (str, optional):
                The IP address of the device making the transaction. Defaults to None.
                  
            - transaction_ref (str):
                Unique reference for the transaction. Defaults to the reference used in the initiated transaction (self).
                
        Returns:
            - dict:
                Detailed transaction information from the API, including the result of the transaction processing.
        """
        self.rsa_key = get_rsa(self.rsa_key)
        transaction_ref = get_transaction_ref(transaction_ref, self.transaction_ref)
        payload = {
            "payload": encrypt_card(cardDetails, self.rsa_key),
            "transactionReference": transaction_ref,
            "deviceDetails": {
                "payerDeviceDto": {
                    "device": {
                        "browser": browserDetails.get('User-Agent'),
                        "browserDetails": {
                            "3DSecureChallengeWindowSize": browserDetails.get('3DSecureChallengeWindowSize', 'FULL_SCREEN'),
                            "acceptHeaders": "application/json",
                            "colorDepth": browserDetails.get('colorDepth'),
                            "javaEnabled": browserDetails.get('javaEnabled'),
                            "language": browserDetails.get('language'),
                            "screenHeight": browserDetails.get('screenHeight'),
                            "screenWidth": browserDetails.get('screenWidth'),
                            "timeZone": browserDetails.get('timeZone')
                        },
                        "ipAddress": ipAddress
                    }
                }
            }
        }
        response = send_payment_request(cardUrl, payload, self.headers)
        self.gatewayReference = response.get('responseBody', {}).get('gatewayReference')
        return response

    def resend_otp(self, transaction_ref: str = None, gatewayReference: str = None) -> dict:
        """
        Resends an OTP for a specific transaction.

        Args:
            transaction_ref (str): Unique reference for the transaction. Defaults to the reference used in the initiated transaction (self).
            gatewayReference (str): Gateway reference for the transaction. Defaults to the gateway reference used in the initiated transaction (self).

        Returns:
            dict: Response from the API after resending the OTP.
        """
        transaction_ref = get_transaction_ref(transaction_ref, self.transaction_ref)
        gatewayReference = get_gateway_ref(gatewayReference, self.gatewayReference)
        return send_payment_request(f"{resendOptUrl}/{transaction_ref}", {'gatewayReference': gatewayReference, 'amount': '100050'}, self.headers)

    def submit_otp(self, otp: str, transaction_ref: str = None, gatewayReference: str = None) -> dict:
        """
        Submits an OTP for a specific transaction to complete the process.

        Args:
            otp (str): The OTP provided by the customer.
            transaction_ref (str): Unique reference for the transaction. Defaults to the reference used in the initiated transaction (self).
            gatewayReference (str): Gateway reference for the transaction. Defaults to the gateway reference used in the initiated transaction (self).

        Returns:
            dict: Response from the API after submitting the OTP.
        """
        transaction_ref = get_transaction_ref(transaction_ref, self.transaction_ref)
        gatewayReference = get_gateway_ref(gatewayReference, self.gatewayReference)
        return send_payment_request(f"{submitOptUrl}/{transaction_ref}", {'gatewayReference': gatewayReference, 'otp': otp}, self.headers)



