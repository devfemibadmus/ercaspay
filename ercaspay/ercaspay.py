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
    def __init__(self, rsa_key: str = None, env: str = ".env", token: str = None):
        self.token = token or get_token(env)
        self.rsa_key = get_rsa(rsa_key)
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
        return send_payment_request(cardUrl, payload, self.headers)



import secrets, uuid, datetime
from typing import Callable, Dict
from flask import Flask, render_template, Blueprint, session, request, abort, redirect

class ErcaspayPage:
    """
    ErcaspayPage integrates the Ercaspay payment gateway into a Flask application.
    
    This class sets up routes and functionality for initiating and verifying transactions
    with the Ercaspay API. It manages CSRF protection, transaction initiation, and the
    handling of callback authentication for completed transactions.

    Attributes:
        ercaspay (Ercaspay): Instance of the Ercaspay API client.
        name (str): Name of the payment page.
        description (str): Description of the payment page.
        no_phone (bool): Indicates if phone number is optional during payment.
        redirect_url (str): URL to redirect users after payment authentication.
        create_transaction (Callable): Callback function to process transaction details.
    """

    def __init__(self, app: Flask, name: str, description: str = '', no_phone: bool = True,
                 redirect_url: str = '/', auth_redirect_url: str = '/ercaspay/auth', rsa_key: str = None,
                 env: str = ".env", token: str = None, create_transaction: Callable[[Dict], None] = None):
        """
        Initializes the ErcaspayPage instance and registers it with the Flask app.

        Args:
            app (Flask): The Flask application instance.
            name (str): Name of the payment page.
            description (str): Description of the payment page.
            no_phone (bool): If True, phone number is not required for payment.
            redirect_url (str): URL to redirect users after successful authentication.
            auth_redirect_url (str): URL for Ercaspay authentication callbacks.
            rsa_key (str): Path to RSA key file for secure communications.
            env (str): Environment file or environment variable for API configurations.
            token (str): API token for the Ercaspay service.
            create_transaction (Callable): Callback function to handle transaction creation.
        """
        self.ercaspay = Ercaspay(rsa_key, env, token)
        self.name = name
        self.description = description
        self.no_phone = no_phone
        self.redirect_url = redirect_url
        self.create_transaction = create_transaction
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """
        Initializes the Flask app with ErcaspayPage routes and configurations.

        Args:
            app (Flask): The Flask application instance to configure.
        """
        blueprint = Blueprint('ercaspay', __name__, static_folder='ercaspay_static', template_folder='ercaspay_template')
        app.register_blueprint(blueprint)

        @app.before_request
        def generate_csrf_token():
            """
            Generates a CSRF token for session-based protection against CSRF attacks.
            """
            if "csrf_token" not in session:
                session["csrf_token"] = secrets.token_hex(16)

        @app.route("/ercaspay", methods=["GET", "POST"])
        def payment_page():
            """
            Displays the payment page and handles payment initiation requests.

            Returns:
                - On GET: Renders the payment page template.
                - On POST: Initiates a payment request and redirects to the checkout URL.

            Raises:
                403: If CSRF token validation fails.
                400: If required fields are missing.
                HTTPException: For API-related errors.
            """
            website = {'name': self.name, 'description': self.description, 'no_phone': self.no_phone}
            if request.method == "POST":
                token = request.form.get("csrf_token")
                valid = token and token == session.get("csrf_token")
                session.pop("csrf_token", None)
                if not valid:
                    abort(403)
                first_name = request.form.get('first_name')
                last_name = request.form.get('last_name')
                full_name = f'{first_name} {last_name}'
                email = request.form.get('email')
                amount = request.form.get('amount')
                phone_number = None
                if not website['no_phone']:
                    phone_number = request.form.get('phone_number')
                required_fields = ['first_name', 'last_name', 'email', 'amount']
                if not website['no_phone']:
                    required_fields.append('phone_number')
                if not all(request.form.get(field) for field in required_fields):
                    abort(400)
                auth_url = f'{request.host_url}ercaspay/auth'
                paymentReference = f"{uuid.uuid4().hex}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                response = self.ercaspay.initiate(amount, full_name, email, paymentReference, None, phone_number, auth_url)
                checkoutUrl = response.get('responseBody', {}).get('checkoutUrl')
                if checkoutUrl is not None:
                    return redirect(checkoutUrl)
                abort(response['errorCode'], description=response['errorMessage'])
            return render_template('payment.html', website=website, csrf_token=session["csrf_token"])

        @app.route("/ercaspay/auth", methods=["GET"])
        def auth_page():
            """
            Handles the authentication callback from Ercaspay.

            Returns:
                - Redirects to the configured redirect_url after successful transaction verification.

            Raises:
                400: If the transaction reference is missing.
                HTTPException: For API-related errors.
            """
            transRef = request.args.get('transRef')
            if transRef:
                response = self.ercaspay.verify(transRef)
                if response.get('errorCode'):
                    abort(response['errorCode'], description=response['errorMessage'])
                status = response.get('responseBody', {}).get('status')
                # print(response)
                if status:
                    self.create_transaction(response)
                return redirect(self.redirect_url)
            abort(400)


