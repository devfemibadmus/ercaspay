import os, sys, requests
from typing import Optional


valid_payment_methods = ['card', 'bank-transfer', 'qrcode', 'ussd']


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
        env (Optional[str]): Path to the environment file. Defaults to '.env'.

    Returns:
        str: The authorization token.

    Raises:
        FileNotFoundError: If the environment file is not found.
        ValueError: If no 'Authorization' token is found.
    """
    if env and not os.path.exists(env):
        raise FileNotFoundError(f"Environment file '{env}' not found.")
    load_env_vars(env or '.env')
    token = os.environ.get('Authorization')
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


def handle_payment_status(status_code: str, resp: dict) -> dict:
    """
    Maps status codes to their corresponding messages and explanations.
    
    Args:
        status_code (str): The status code received from the payment API response.
        
    Returns:
        dict: A dictionary with errorCode as the key and the error message with explanation as the value.
    """
    status_messages = {
        '401': {'message': 'Unauthorized', 'explanation': 'Authentication error. Please verify your API key or token.'},
        '403': {'message': 'Forbidden', 'explanation': 'You do not have permission to perform this action.'},
        '404': {'message': 'Not Found', 'explanation': 'The requested resource could not be found.'},
    }
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
        # '500': 'Internal Server Error',
        '504': 'Gateway Timeout',
        '507': 'Insufficient Storage',
        '511': 'Network Authentication Required'
    }
    
    if status_code in status_messages:
        return { 'errorCode': status_code, 'message': status_messages[status_code]['message'], 'explanation': status_messages[status_code]['explanation'] }
    
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
        return handle_payment_status(str(response.status_code), response.json())
    except requests.exceptions.RequestException as e:
        return {'errorCode': 'RequestException', 'message': 'Error sending request', 'explanation': str(e)}




