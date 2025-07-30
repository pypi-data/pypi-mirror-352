# AgentPaid Python SDK

Official Python SDK for the AgentPaid API.

## Installation

```bash
pip install Paid.ai-Client
```

## Usage

```python
from paid_client import PaidClient

# Initialize the client
client = PaidClient(
    api_key='YOUR_API_KEY',
    api_url='YOUR_API_URL'  # Optional, defaults to production URL
)

# Example: Record usage
client.record_usage(
    'agent_id',
    'customer_id',
    'event_name',
    {'key': 'value'}
)
# Signals are automatically flushed:
# - Every 30 seconds
# - When the buffer reaches 100 events
# To manually flush:
client.flush()
```

## API Documentation

### Usage Recording
- `record_usage(agent_id: str, external_user_id: str, signal_name: str, data: Any) -> None`
- `flush() -> None`

### Accounts
- `create_account(data: CreateAccountRequest) -> Account`
- `get_account(account_id: str) -> Account`
- `get_account_by_external_id(external_id: str) -> Account`
- `list_accounts() -> List[Account]`
- `update_account(account_id: str, data: UpdateAccountRequest) -> Account`
- `update_account_by_external_id(external_id: str, data: UpdateAccountRequest) -> Account`
- `delete_account(account_id: str) -> None`
- `delete_account_by_external_id(external_id: str) -> None`

### Orders
- `create_order(data: CreateOrderRequest) -> Order`
- `get_order(order_id: str) -> Order`
- `list_orders() -> List[Order]`
- `add_order_lines(order_id: str, lines: List[Dict[str, Any]]) -> List[OrderLine]`
- `activate_order(order_id: str) -> str`
- `delete_order(order_id: str) -> None`

### Agents
- `create_agent(agent: CreateAgentRequest) -> Agent`
- `get_agent(agent_id: str) -> Agent`
- `get_agent_by_external_id(external_id: str) -> Agent`
- `list_agents() -> List[Agent]`
- `update_agent(agent_id: str, data: UpdateAgentRequest) -> Agent`
- `update_agent_by_external_id(external_id: str, data: UpdateAgentRequest) -> Agent`
- `delete_agent(agent_id: str) -> None`
- `delete_agent_by_external_id(external_id: str) -> None`

### Contacts
- `create_contact(data: CreateContactRequest) -> Contact`
- `get_contact(contact_id: str) -> Contact`
- `get_contact_by_external_id(external_id: str) -> Contact`
- `list_contacts(account_id: Optional[str] = None) -> List[Contact]`
- `delete_contact(contact_id: str) -> str`
- `delete_contact_by_external_id(external_id: str) -> str`
