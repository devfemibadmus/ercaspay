from flask import Flask, render_template
from ercaspay import ErcaspayPage
from typing import Dict

app = Flask(__name__)
app.secret_key = "your-secret-key"
    

def create_transaction(data: Dict):
    response_body = data.get('responseBody', {})
    domain = response_body.get('domain')
    status = response_body.get('status')
    ercs_reference = response_body.get('ercs_reference')
    tx_reference = response_body.get('tx_reference')
    amount = response_body.get('amount')
    description = response_body.get('description')
    paid_at = response_body.get('paid_at')
    created_at = response_body.get('created_at')
    channel = response_body.get('channel')
    currency = response_body.get('currency')
    fee = response_body.get('fee')
    fee_bearer = response_body.get('fee_bearer')
    settled_amount = response_body.get('settled_amount')
    customer = response_body.get('customer', {})
    customer_name = customer.get('name')
    customer_phone = customer.get('phone_number')
    customer_email = customer.get('email')
    customer_reference = customer.get('reference')
    
    print(f"Domain: {domain}, Status: {status}, Amount: {amount}, Customer: {customer_name}")


hello_extension = ErcaspayPage(app, "Sponsor Scholarship Contribution", create_transaction=create_transaction)

@app.route("/")
def hello_world():
    return render_template("a.html")

if __name__ == "__main__":
    app.run(debug=True)
