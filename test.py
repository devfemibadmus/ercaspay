import secrets
import uuid, datetime
from typing import Callable, Dict
from ercaspay import Ercaspay
from flask import Flask, render_template, Blueprint, session, request, abort, redirect

class ErcaspayPage:
    def __init__(self, app: Flask, name: str, description: str = '', no_phone: bool = True, redirect_url: str = '/', auth_redirect_url: str = '/ercaspay/auth',  rsa_key: str = None, env: str = ".env", token: str = None, create_transaction: Callable[[Dict], None] = None):
        self.ercaspay = Ercaspay(rsa_key, env, token)
        self.name = name
        self.description = description
        self.no_phone = no_phone
        self.redirect_url = redirect_url
        self.create_transaction = create_transaction
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        blueprint = Blueprint('ercaspay', __name__, static_folder='ercaspay_static', template_folder='ercaspay_template')
        app.register_blueprint(blueprint)
        
        @app.before_request
        def generate_csrf_token():
            if "csrf_token" not in session:
                session["csrf_token"] = secrets.token_hex(16)
        
        @app.route("/ercaspay", methods=["GET", "POST"])
        def payment_page():
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
            transRef = request.args.get('transRef')
            if transRef:
                response = self.ercaspay.verify(transRef)
                if response.get('errorCode'):
                    abort(response['errorCode'], description=response['errorMessage'])
                status = response.get('responseBody', {}).get('status')
                print(response)
                if status:
                    self.create_transaction(response)
                return redirect(self.redirect_url)
            abort(400)
                    
                    
                
