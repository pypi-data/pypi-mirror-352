# Vaults.fyi Python SDK

A Python SDK for interacting with the Vaults.fyi API. This package provides feature-equivalent functionality to the JavaScript SDK with Pythonic naming conventions.

## Installation

```bash
pip install vaultsfyi
```

## Quick Start

```python
from vaultsfyi import VaultsSdk

# Initialize the SDK
client = VaultsSdk(api_key="your_api_key_here")

# Get user's idle assets
idle_assets = client.get_idle_assets("0x742d35Cc6543C001")

# Get best deposit options (filtered for USDC/USDS)
deposit_options = client.get_deposit_options(
    "0x742d35Cc6543C001",
    allowed_assets=["USDC", "USDS"]
)

# Get user positions
positions = client.get_positions("0x742d35Cc6543C001")

# Generate deposit transaction
transaction = client.get_actions(
    action="deposit",
    user_address="0x742d35Cc6543C001",
    network="mainnet",
    vault_address="0x...",
    amount="1000000",
    asset_address="0x...",
    simulate=False
)
```

## API Methods

### Portfolio Methods
- `get_positions(user_address, **kwargs)` - Get all user positions
- `get_deposit_options(user_address, allowed_assets=None, **kwargs)` - Get best deposit options
- `get_idle_assets(user_address, **kwargs)` - Get user's idle/available balances
- `get_vault_holder_events(user_address, network, vault_address, **kwargs)` - Get vault events
- `get_vault_total_returns(user_address, network, vault_address, **kwargs)` - Get total returns

### Vault Methods
- `get_all_vaults(**kwargs)` - Get all available vaults
- `get_vault(network, vault_address, **kwargs)` - Get specific vault details
- `get_vault_historical_data(network, vault_address, **kwargs)` - Get historical data

### Transaction Methods
- `get_actions(action, user_address, network, vault_address, **kwargs)` - Generate transactions
- `get_transactions_context(user_address, network, vault_address, **kwargs)` - Get transaction context

### Other Methods
- `get_benchmarks()` - Get benchmark data



## Error Handling

The SDK provides specific exception types:

```python
from vaultsfyi import VaultsSdk, HttpResponseError, AuthenticationError

try:
    client = VaultsSdk(api_key="invalid_key")
    result = client.get_benchmarks()
except AuthenticationError:
    print("Invalid API key")
except HttpResponseError as e:
    print(f"API error: {e}")
```

## Requirements

- Python 3.8+
- requests


## License

MIT License

## Author

Kaimi Seeker (kaimi@wallfacer.io)