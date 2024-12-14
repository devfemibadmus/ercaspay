import os
import requests
from typing import Optional
from .utility import *

class Ercaspay:
    def __init__(self, env: str=None, token: str=None, baseUrl: str=None):
        self.baseUrl = baseUrl or 'https://api.merchant.staging.ercaspay.com/api/v1'
        self.verifyUrl = f"{self.baseUrl}/payment/transaction/verify"
        self.initiateUrl = f"{self.baseUrl}/payment/initiate"
        self.detailsUrl = f"{self.baseUrl}/payment/details"
        self.cancelUrl = f"{self.baseUrl}/payment/cancel"
        self.statusUrl = f"{self.baseUrl}/payment/status"
        self.token = token or get_token(env)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def initiate_Transaction(self, amount: float, customerName: str, customerEmail: str, 
        paymentReference: str, paymentMethods: str = None, 
        customerPhoneNumber: str = None, redirectUrl: str = None, 
        description: str = None, metadata: str = None, 
        feeBearer: str = None, currency: str = 'NGN'):
        """
        Initiate a payment transaction.

        Args:
            - amount (float): The amount to be paid by the customer (mandatory).
            - paymentReference (str): Merchant's unique reference for the transaction (mandatory).
            - paymentMethods (str, optional): Comma-separated string of payment methods (e.g., 'card, bank-transfer, qrcode, ussd').
              If not specified, all available payment methods enabled on the merchant dashboard will be used.
            - customerName (str): Full name of the customer (mandatory).
            - customerEmail (str): Email address of the customer (mandatory).
            - customerPhoneNumber (str, optional): Phone number of the customer.
            - redirectUrl (str, optional): A URL to redirect the user to after completing the payment.
              If not specified, the default merchant redirect URL will be used.
            - description (str, optional): A description for the transaction.
            - metadata (str, optional): Additional information related to the transaction. This will be returned in the webhook.
            - feeBearer (str, optional): The bearer of the charge (either 'customer' or 'merchant').
              If not specified, the default setting on the merchant account will be used.
            - currency (str, optional): The currency in which the payment will be made (default is 'NGN').
              A list of supported currencies is available on the merchant's landing page.

        Returns (example):
            Failure: {'errorCode': '422', 'message': 'Failed', 'explanation': 'The amount cannot be less than 100 NGN.'}
            
            Success: {'requestSuccessful': True, 'responseCode': 'success', 'responseMessage': 'success', 'responseBody': {'paymentReference': 'nigga@example.com', 'transactionReference': 'ERCS|20241213224108|1734126068287', 'checkoutUrl': 'https://sandbox-checkout.ercaspay.com/ERCS|20241213224108|1734126068287'}}
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
            "feeBearer": feeBearer
        }
        return send_payment_request(self.initiateUrl, payload=payload, headers=self.headers)
      
    def cancel_transaction(self, transaction_ref: str) -> dict:
        """
        Cancel a transaction that has not yet been marked as completed.

        Args:
            transaction_ref (str): The reference ID of the transaction to be canceled.

        Returns (example):
            Failure: {'errorCode': '404', 'message': 'Not Found', 'explanation': 'The requested resource could not be found.'}
            
            Success: {'requestSuccessful': True, 'responseCode': 'success', 'responseMessage': 'success', 'responseBody': {'callback_url': 'https://nigga.com?reference=nigga@example.com&status=CANCELLED'}}
        """
        return send_payment_request(f"{self.cancelUrl}/{transaction_ref}", {}, self.headers)
    
    def verify_transaction(self, transaction_ref: str) -> dict:
        """
        We highly recommend that when you receive a notification from us, you should initiate a verify transaction request to us to confirm the actual status of that transaction before updating the records on your database.

        Args:
            transaction_ref (str): The reference ID of the transaction to be canceled.

        Returns (example):
            Failure: {'errorCode': '400', 'message': 'Bad Request', 'explanation': 'This payment was cancelled'}
            
            Success: {'requestSuccessful': True, 'responseCode': 'success', 'responseMessage': 'success', 'responseBody': {'callback_url': 'https://nigga.com?reference=nigga@example.com&status=CANCELLED'}}
        """
        return send_payment_request(f"{self.verifyUrl}/{transaction_ref}", {}, self.headers)

    def details_transaction(self, transaction_ref: str) -> dict:
        """
        Obtain detailed information about a specific transaction identified by its unique transaction ID.

        Args:
            transaction_ref (str): The reference ID of the transaction to be canceled.

        Returns (example):
            Failure: {'errorCode': '400', 'message': 'Unknown error', 'explanation': 'This payment was cancelled, please initiate a new payment'}
            
            Success: {'requestSuccessful': True, 'responseCode': 'success', 'responseMessage': 'success', 'responseBody': {'customerName': 'test', 'customerEmail': 'nigga@example.com', 'amount': 100.55, 'businessName': "Dev's App", 'businessLogo': None, 'whiteLabel': None, 'paymentMethods': ['card', 'bank-transfer', 'qrcode', 'ussd']}}
        """
        return send_payment_request(f"{self.detailsUrl}/{transaction_ref}", {}, self.headers)
    
    def status_transaction(self, transaction_ref: str, reference: str=None, payment_method: str=None) -> dict:
        """
        Check transaction status, this might be faster in sense whereby u know they payment_method e.g the frontend will knows

        Args:
            transaction_ref (str): The reference ID of the transaction to be canceled.

        Returns (example):
            Failure: {'errorCode': '404', 'message': 'Not Found', 'explanation': 'The requested resource could not be found.'}
            
            Success: {'requestSuccessful': True, 'responseCode': 'success', 'responseMessage': 'success', 'responseBody': {'paymentReference': 'nigga@example.com', 'amount': 100.55, 'status': 'PAID', 'description': None, 'callbackUrl': 'https://nigga.com?reference=nigga@example.com&status=PAID&transRef=ERCS|20241214001647|1734131807931'}}
        """
        payment_method = payment_method.strip().lower() if payment_method else 'bank-transfer'
        if payment_method not in valid_payment_methods:
            payment_method = 'bank-transfer'
        payload = {
            'payment_method': payment_method,
            'reference': reference,
        }
        return send_payment_request(f"{self.statusUrl}/{transaction_ref}", payload, self.headers)


