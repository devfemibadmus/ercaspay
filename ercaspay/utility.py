"""
This module provides a comprehensive set of utilities for interacting with a payment API. 

It includes functionality for:
- Loading environment variables.
- Validating and formatting payment methods and currencies.
- Sending payment requests and handling responses.
- Encrypting card details with RSA.
- Managing transaction references.
- Checking supported banks for USSD transfers.

Constants:
    - `valid_payment_methods`: Default payment methods available.
    - `baseUrl`: Base URL for the payment API.
    - Various endpoint URLs for specific payment actions (`bankUrl`, `verifyUrl`, etc.).

Functions:
    - `load_env_vars(env_file_path)`: Loads environment variables from a specified file.
    - `get_token(env=None)`: Retrieves the authorization token from the environment.
    - `formatCurrency(currency_name)`: Converts currency names to their corresponding codes.
    - `formatPaymentMethods(payment_method)`: Normalizes and validates payment methods.
    - `handle_error_msg(status_code, resp)`: Maps status codes to user-friendly error messages.
    - `send_payment_request(url, payload, headers)`: Sends payment requests and handles errors.
    - `get_rsa(key_input)`: Loads an RSA public key from input or environment variables.
    - `encrypt_card(card_details, rsa_public_key)`: Encrypts card details using RSA encryption.
    - `get_transaction_ref(transaction_ref, self_transaction_ref)`: Resolves transaction references.
    - `supported_banks()`: Retrieves a list of supported banks for USSD transfers.
    - `support_bank(bank_name)`: Checks if a specified bank is supported.

Dependencies:
    - `os`: For environment variable management.
    - `requests`: For sending HTTP requests.
    - `json`: For handling JSON data.
    - `base64`: For encoding encrypted card details.
    - `Crypto.PublicKey.RSA` and `Crypto.Cipher.PKCS1_v1_5`: For RSA key management and encryption.

Usage:
    Import this module into your application to interact with the ERCASPAY API. 
    Example:
        from main import get_token, send_payment_request

        token = get_token(".env")
        response = send_payment_request(bankUrl, {}, {"Authorization": token})
"""

import os, requests, json, base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

valid_payment_methods = ['card', 'bank-transfer', 'qrcode', 'ussd'] # not effective only use as default if user pass none and also use in checking transaction status(not validated)

# valid_bank_names = ["access", "alat", "ecobank", "fcmb", "fidelity", "firstbank", "gtbank", "heritage", "keystone", "polaris", "stanbic", "sterling", "uba", "union", "unity", "wema", "zenith"]


baseUrl = "https://api.merchant.staging.ercaspay.com/api/v1"
bankUrl = f"{baseUrl}/payment/bank-transfer/request-bank-account"
verifyUrl = f"{baseUrl}/payment/transaction/verify"
cardUrl = f"{baseUrl}/payment/cards/initialize"
initiateUrl = f"{baseUrl}/payment/initiate"
detailsUrl = f"{baseUrl}/payment/details"
cancelUrl = f"{baseUrl}/payment/cancel"
statusUrl = f"{baseUrl}/payment/status"
ussdUrl = f"{baseUrl}/payment/ussd"

def load_env_vars(env_file_path):
    """
    Loads environment variables from a specified file.
    
    Args:
        env_file_path (str): Path to the environment file.
    
    Raises:
        FileNotFoundError: If the environment file is not found.
    """
    if not os.path.exists(env_file_path):
        raise FileNotFoundError(f"Environment file '{env_file_path}' not found.")
    with open(env_file_path, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value


def get_token(env: str = None):
    """
    Retrieves the 'Authorization' token from the environment.

    Args:
        env (str): Path to the environment file. Defaults to '.env'.

    Returns:
        str: The authorization token.

    Raises:
        FileNotFoundError: If the environment file is not found.
        ValueError: If no 'Authorization' token is found.
    """
    if env and not os.path.exists(env):
        raise FileNotFoundError(f"Environment file '{env}' not found.")
    load_env_vars(env or '.env')
    token = os.environ.get('ERCASPAY_AUTHORIZATION')
    if not token:
        raise ValueError(f"No 'Authorization' found in {env or '.env'}")
    return token


def formatCurrency(currency_name: str = None):
    """
    Convert the currency name to the corresponding currency code.
        
    Args:
        currency_name (str): The currency name (e.g., 'USD', 'NGN').

    Returns:
        str: The corresponding currency code if valid, else raises a ValueError.
    """
    currency_map = {
        'ngn': 'NGN',
        'usd': 'USD',
        'cad': 'CAD',
        'gbp': 'GBP',
        'gh₵': 'GH₵',
        'gmd': 'GMD',
        'ksh': 'Ksh',
        'euro': 'EURO'
    }

    currency_name = currency_name.lower()
        
    if currency_name not in currency_map:
        raise ValueError(f"Unsupported currency: {currency_name}")
        
    return currency_map[currency_name]


def formatPaymentMethods(payment_method: str) -> str:
    """
    Normalizes and validates payment method input.

    Args:
        payment_method (str): The payment method entered by the user.

    Returns:
        str: The standardized payment method (e.g., 'card', 'bank-transfer', 'qrcode', 'ussd').
        None: If the payment method is not valid.
    """
    if payment_method:
        payment_method = payment_method.strip().lower()
        if payment_method in valid_payment_methods:
            return payment_method
        if 'bank' in payment_method and 'transfer' in payment_method:
            return 'bank-transfer'
    return ', '.join(valid_payment_methods)


def handle_error_msg(status_code: str, resp: dict) -> dict:
    """
    Maps status codes to their corresponding messages and explanations.
    
    Args:
        status_code (str): The status code received from the payment API response.
        
    Returns:
        dict: A dictionary with errorCode as the key and the error message with explanation as the value.
    """
    error_codes = {
        '400': 'Bad Request',
        '401': 'Unauthorized',
        '403': 'Forbidden',
        '404': 'Not Found',
        '405': 'Method Not Allowed',
        '408': 'Request Timeout',
        '409': 'Conflict',
        '410': 'Gone',
        '422': 'Unprocessable',
        '429': 'Too Many Requests',
        '500': 'Internal Server Error',
        '504': 'Gateway Timeout',
        '507': 'Insufficient Storage',
        '511': 'Network Authentication Required'
    }
    
    return { 'errorCode': status_code, 'message': error_codes.get(status_code, 'Unknown error'), 'explanation': resp.get('errorMessage', 'Something went wrong on our end.') }


def send_payment_request(url: str, payload: dict, headers: dict) -> dict:
    """
    Sends a payment request to the specified URL and handles any potential errors.

    Args:
        url (str): The endpoint to send the request to.
        payload (dict): The data to be sent in the POST request.
        headers (dict): The headers to include in the request.
        
    Returns:
        dict: The response from the server in JSON format or an error message with code and explanation.
    """
    try:
        if not payload:
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, json=payload, headers=headers)
        # print(response.json())
        # print(response.status_code)
        if response.status_code in [200, 201]:
            return response.json()
        return handle_error_msg(str(response.status_code), response.json())
    except requests.exceptions.RequestException as e:
        return {'errorCode': 'RequestException', 'message': 'Error sending request', 'explanation': str(e)}


def get_rsa(key_input: str = None):
    """
    Loads and returns an RSA public key based on the provided input.

    Args:
        key_input (str or None): The input for the RSA key. It can be:
            - A string containing the RSA public key.
            - A file path to the public key file.
            - None, in which case the function will attempt to load the key from the 
              environment variable `ERCASPAY_PUBLIC_KEY`.

    Returns:
        RSA key object: The RSA public key object.

    Raises:
        ValueError: If the RSA key cannot be loaded from the provided input or the 
                    environment variable.
    """
    try:
        if key_input is None:
            rsa_public_key = os.environ.get('ERCASPAY_PUBLIC_KEY')
            if rsa_public_key:
                rsa_public_key = f"-----BEGIN PUBLIC KEY-----\n{rsa_public_key.strip()}\n-----END PUBLIC KEY-----"
                return RSA.import_key(rsa_public_key)
            else:
                raise ValueError("No RSA key provided and environment variable is missing.")

        if os.path.isfile(key_input):
            with open(key_input, "rb") as key_file:
                return RSA.import_key(key_file.read())
        else:
            raise ValueError(f"The provided path to the RSA key does not exist or is invalid: {os.path.abspath(key_input)}")
        
        return RSA.import_key(key_input)

    except Exception as e:
        raise ValueError(f"Failed to load RSA key: {str(e)}")


def encrypt_card(card_details: dict, rsa_public_key: str) -> str:
    card_json = json.dumps(card_details).encode("utf-8")
    cipher = PKCS1_v1_5.new(rsa_public_key)
    encrypted = cipher.encrypt(card_json)
    return base64.b64encode(encrypted).decode("utf-8")


def get_transaction_ref(transaction_ref: str, self_transaction_ref: str):
    if transaction_ref is None:
        if self_transaction_ref is None:
            raise ValueError("Transaction reference is required. Please provide a valid transaction reference or initiate the transaction.")
        return self_transaction_ref
    return transaction_ref


def supported_banks() -> dict:
    """
    Get all the supported banks for USSD transfer

    Returns:
        dict: Response containing the USSD code and related details.
    """
    return send_payment_request(f"{ussdUrl}/supported-banks", {}, {})


def support_bank(bank_name: str) -> bool:
    """
    Check if a bank is supported
    
    Args:
        bank_name(str): name of the bank e.g Fcmb

    Returns:
        bool: Response True or False.
    """
    supported_bank_list = supported_banks()
    return bank_name.lower() in [bank.lower() for bank in supported_bank_list.get('responseBody', [])]


