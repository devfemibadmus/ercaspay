"""
Ercaspay Python Client

This module provides a Python client for interacting with the Ercaspay API, allowing for initiating, verifying, cancelling, and processing payment transactions. The client supports various payment methods, including USSD, bank transfers, and card payments, and offers utility functions for managing supported banks and payment statuses.

Classes:
    Ercaspay: Main class for interacting with the Ercaspay API.

Functions:
    __init__(self, rsa_key: str = None, env: str = ".env", token: str = None):
        Initializes the Ercaspay client with the RSA public key, environment file, and authorization token.

    initiate(self, amount: float, customerName: str, customerEmail: str, paymentReference: str, paymentMethods: str = None, customerPhoneNumber: str = None, redirectUrl: str = None, description: str = None, metadata: str = None, feeBearer: str = None, currency: str = "NGN") -> dict:
        Initiates a payment transaction on the Ercaspay platform.

    cancel(self, transaction_ref: str = None) -> dict:
        Cancels an ongoing or scheduled transaction on Ercaspay.

    verify(self, transaction_ref: str = None) -> dict:
        Verifies the status of a transaction using its reference.

    details(self, transaction_ref: str = None) -> dict:
        Retrieves detailed information about a specific transaction.

    status(self, transaction_ref: str = None, reference: str = None, payment_method: str = None) -> dict:
        Checks the payment status of a specific transaction.

    ussd(self, bank_name: str, transaction_ref: str = None, amount: float = None) -> dict:
        Generates a USSD code for a transaction, allowing customers to complete payment via USSD.

    supported_bank_list(self) -> dict:
        Retrieves a list of supported banks for USSD transfers.

    support_bank(self, bank_name: str) -> bool:
        Checks if a given bank is supported for USSD transfers.

    bank(self, transaction_ref: str = None) -> dict:
        Generates bank details for a transaction, allowing customers to complete payment via transfer.

    card(self, cardDetails: dict, browserDetails: dict, ipAddress: str = None, transaction_ref: str = None) -> dict:
        Processes a card transaction using card details, browser details, and optional IP address.

Notes:
    - The RSA key can be provided directly as a string or as a file path.
    - Environment variables and `.env` files are used for configuration and token retrieval.
    - Example env
        - ERCASPAY_AUTHORIZATION=ECRS-LIVE-SKNvIyOB5m62L7867074LXvHyeMGyYQT4WF
        - ERCASPAY_PUBLIC_KEY=MIIBIjANBgkqh+XteF77303qsAvgYFF4B6OmVtYD7QezLWvVlU0h7oXc9fCz2V+23B6gRUZjmNxE3FMIUhNIb9eqR+rl3w

Example Usage:
    ```python
    from ercaspay import Ercaspay

    ercaspay = Ercaspay(rsa_key="path/to/rsa_key", env=".env")

    # Initiating a transaction
    transaction = ercaspay.initiate(
        amount=1000.0,
        customerName="John Doe",
        customerEmail="john.doe@example.com",
        paymentReference="REF12345",
        currency="NGN"
    )
    print(transaction)

    # Verifying a transaction
    transaction_status = transaction.status()
    print(transaction_status)
    ```

Learn more: https://github.com/devfemibadmus/ercaspay
"""

from .utility import *
from .ercaspay import Ercaspay

