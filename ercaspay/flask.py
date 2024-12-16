import secrets, uuid, datetime
from .main import Ercaspay
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
                 redirect_url: str = '/', auth_redirect_url: str = '/ercaspay/auth', ercaspay_url: str = '/ercaspay', rsa_key: str = None,
                 env: str = ".env", token: str = None, create_transaction: Callable[[Dict], None] = None, admin_url: str = "/", currency: str = "NGN"):
        """
        Initializes the ErcaspayPage instance and registers it with the Flask app.

        Args:
            app (Flask): The Flask application instance.
            name (str): Name of the payment page.
            description (str): Description of the payment page.
            no_phone (bool): If True, phone number is not required for payment.
            redirect_url (str): URL to redirect users after successful authentication.
            ercaspay_url (str): URL for Ercaspay payment Page.
            auth_redirect_url (str): URL for Ercaspay authentication callbacks.
            rsa_key (str): Path to RSA key file for secure communications.
            env (str): Environment file or environment variable for API configurations.
            token (str): API token for the Ercaspay service.
            create_transaction (Callable): Callback function to handle transaction creation.
            admin_url (str): ercaspay admin page, default is $this.website.
            currency (str): collect payment in differents currency default (NGN).
        """
        self.ercaspay = Ercaspay(rsa_key, env, token)
        self.name = name
        self.description = description
        self.no_phone = no_phone
        self.redirect_url = redirect_url
        self.admin_url = admin_url
        self.currency = currency
        self.ercaspay_url = ercaspay_url
        self.auth_redirect_url = auth_redirect_url
        self.create_transaction = create_transaction
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """
        Initializes the Flask app with ErcaspayPage routes and configurations.

        Args:
            app (Flask): The Flask application instance to configure.
        """
        blueprint = Blueprint('ercaspay', __name__, static_folder='static', template_folder='templates')
        app.register_blueprint(blueprint, url_prefix='/ercaspay')

        @app.before_request
        def generate_csrf_token():
            """
            Generates a CSRF token for session-based protection against CSRF attacks.
            """
            if "csrf_token" not in session:
                session["csrf_token"] = secrets.token_hex(16)

        @app.route(self.ercaspay_url, methods=["GET", "POST"])
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
                response = self.ercaspay.initiate(amount, full_name, email, paymentReference, None, phone_number, auth_url, currency=self.currency)
                checkoutUrl = response.get('responseBody', {}).get('checkoutUrl')
                if checkoutUrl is not None:
                    return redirect(checkoutUrl)
                abort(response['errorCode'], description=response['explanation'])
            return render_template('payment.html', website=website, csrf_token=session["csrf_token"], dj=None)

        @app.route(self.auth_redirect_url, methods=["GET"])
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
                    abort(response['errorCode'], description=response['explanation'])
                status = response.get('responseBody', {}).get('status')
                # print(response)
                if status:
                    self.create_transaction(response)
                return redirect(self.redirect_url)
            abort(400)
        
        @app.route(f"{self.ercaspay_url}/admin", methods=["GET"])
        def admin_page():
            return redirect(self.admin_url)
        
        


