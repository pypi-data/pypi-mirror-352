# OpenBankProject API Python Client

A comprehensive Python client for the OpenBankProject API v5.1.0, providing access to all available endpoints with robust error handling and authentication support.

## Features

- **Complete API Coverage**: Access to all OpenBankProject API v5.1.0 endpoints
- **Multiple Authentication Methods**: Support for both DirectLogin and GatewayLogin
- **Robust Error Handling**: Specific exception types for different error scenarios
- **Type Hints**: Full type annotations for better IDE integration
- **Comprehensive Documentation**: Detailed docstrings and usage examples
- **Modular Design**: Logically organized endpoint groups for easier navigation

## Installation

```bash
# Install from the package directory
pip install -e /path/to/openbankproject_client

# Or install directly from the zip file
pip install openbankproject_client.zip
```

## Quick Start

```python
from openbankproject_client import OpenBankProjectClient

# Initialize with DirectLogin credentials
client = OpenBankProjectClient(
    base_url="https://api.openbankproject.com",
    api_version="v5.1.0",
    username="your_username",
    password="your_password",
    consumer_key="your_consumer_key"
)

# Or initialize with a pre-generated token
client = OpenBankProjectClient(
    base_url="https://api.openbankproject.com",
    api_version="v5.1.0",
    direct_login_token="your_direct_login_token"
)

# Get a list of banks
banks = client.extended_bank.get_banks()
print(f"Found {len(banks.get('banks', []))} banks")

# Get accounts for a specific bank
accounts = client.extended_account.get_private_accounts_at_bank("your_bank_id")
print(f"Found {len(accounts.get('accounts', []))} accounts")

# Get transactions for an account
transactions = client.transaction.get_transactions_for_account(
    "your_bank_id", "your_account_id", "owner"
)
print(f"Found {len(transactions.get('transactions', []))} transactions")
```

## Authentication

The client supports two authentication methods:

### DirectLogin

```python
# Using username, password, and consumer key
client = OpenBankProjectClient(
    username="your_username",
    password="your_password",
    consumer_key="your_consumer_key"
)

# Using a pre-generated token
client = OpenBankProjectClient(
    direct_login_token="your_direct_login_token"
)
```

### GatewayLogin

```python
client = OpenBankProjectClient(
    gateway_login_token="your_gateway_login_token"
)
```

## Error Handling

The client provides specific exception types for different error scenarios:

```python
from openbankproject_client import (
    ApiError, AuthenticationError, ResourceNotFoundError, 
    ValidationError, PermissionError, ServerError
)

try:
    client.extended_bank.get_banks()
except AuthenticationError as e:
    print(f"Authentication error: {e}")
except ResourceNotFoundError as e:
    print(f"Resource not found: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
except PermissionError as e:
    print(f"Permission error: {e}")
except ServerError as e:
    print(f"Server error: {e}")
except ApiError as e:
    print(f"API error: {e}")
```

## Available Endpoint Categories

The client provides access to all OpenBankProject API v5.1.0 endpoints, organized into logical categories:

1. **Account Access**: Manage account access permissions
2. **Account Application**: Handle account applications
3. **Account Holder**: Manage account holders
4. **Account Metadata**: Work with account tags and metadata
5. **Account Public**: Access public account information
6. **API Collection**: Manage API collections
7. **API Configuration**: Configure API settings
8. **API Favorite**: Manage API favorites
9. **API Management**: Advanced API management functions
10. **ATM**: ATM management and information
11. **Branch**: Branch management and information
12. **Card**: Card management and operations
13. **Connector Method**: Manage connector methods
14. **Consent**: Handle consent operations
15. **Counterparty**: Manage counterparties
16. **Counterparty Limits**: Set and manage counterparty limits
17. **Counterparty Metadata**: Work with counterparty metadata
18. **Customer**: Customer management and information
19. **Customer Meeting**: Schedule and manage customer meetings
20. **Customer Message**: Send and receive customer messages
21. **Direct Debit**: Manage direct debits
22. **Dynamic Endpoint**: Work with dynamic endpoints
23. **Dynamic Entity**: Manage dynamic entities
24. **Dynamic Message Doc**: Handle dynamic message documentation
25. **Dynamic Resource Doc**: Manage dynamic resource documentation
26. **Extended Account**: Advanced account operations
27. **Extended Bank**: Advanced bank operations
28. **FX**: Foreign exchange operations
29. **KYC**: Know Your Customer operations
30. **Metric**: Access API metrics
31. **Product**: Product management and information
32. **Role**: Manage roles and entitlements
33. **Scheduled Event**: Work with scheduled events
34. **Scope**: Manage API scopes
35. **Standing Order**: Create and manage standing orders
36. **Transaction**: Transaction operations
37. **Transaction Metadata**: Work with transaction metadata
38. **Transaction Request**: Create and manage transaction requests
39. **User**: User management and operations
40. **User Invitation**: Manage user invitations
41. **View Custom**: Create and manage custom views
42. **View System**: Work with system views
43. **Webhook**: Manage webhooks
44. **WebUI Props**: Configure web UI properties

## Examples

See the `examples.py` file for comprehensive usage examples covering all major endpoint categories.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
