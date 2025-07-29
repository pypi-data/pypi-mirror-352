# API Reference

Complete reference for the ReZEN Python API client. This document covers all available methods, parameters, and return types.

## 📋 Table of Contents

- [Client Initialization](#client-initialization)
- [Transaction Builder API](#transaction-builder-api)
- [Transactions API](#transactions-api)
- [Teams API](#teams-api)
- [Agents API](#agents-api)
- [Exceptions](#exceptions)
- [Data Types & Enums](#data-types-enums)

---

## Client Initialization

### RezenClient

Main entry point for the ReZEN API.

```python
from rezen import RezenClient

# Initialize with environment variable
client = RezenClient()

# Initialize with API key
client = RezenClient(api_key="your_api_key")

# Initialize with custom base URL
client = RezenClient(api_key="your_api_key", base_url="https://custom.api.url")
```

**Parameters:**
- `api_key` (Optional[str]): API key for authentication. If None, uses `REZEN_API_KEY` environment variable
- `base_url` (Optional[str]): Custom base URL for the API

**Properties:**
- `client.transaction_builder` → [TransactionBuilderClient](#transaction-builder-api)
- `client.transactions` → [TransactionsClient](#transactions-api)
- `client.teams` → [TeamsClient](#teams-api)
- `client.agents` → [AgentsClient](#agents-api)

---

## Transaction Builder API

Create and manage transaction builders with full participant and property management.

### Core Transaction Management

#### `create_transaction_builder(builder_type="TRANSACTION")`

Create a new transaction builder.

```python
# Create basic transaction builder
response = client.transaction_builder.create_transaction_builder()
transaction_id = response.get('id')

# Create listing builder
response = client.transaction_builder.create_transaction_builder(
    builder_type="LISTING"
)
```

**Parameters:**
- `builder_type` (str): Type of builder ("TRANSACTION" or "LISTING")

**Returns:** `Dict[str, Any]` - Transaction builder creation response

#### `get_transaction_builder(transaction_id)`

Get details of a specific transaction builder.

```python
builder = client.transaction_builder.get_transaction_builder(transaction_id)
```

**Parameters:**
- `transaction_id` (str): Transaction builder ID

**Returns:** `Dict[str, Any]` - Complete transaction builder data

#### `submit_transaction(transaction_id)`

Submit a transaction builder for processing.

```python
response = client.transaction_builder.submit_transaction(transaction_id)
```

**Parameters:**
- `transaction_id` (str): Transaction builder ID

**Returns:** `Dict[str, Any]` - Submission response

#### `delete_transaction_builder(transaction_id)`

Delete a transaction builder.

```python
response = client.transaction_builder.delete_transaction_builder(transaction_id)
```

### Participants Management

#### `add_buyer(transaction_id, buyer_info)`

Add a buyer to the transaction.

```python
buyer_data = {
    "type": "BUYER",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@email.com",
    "phone": "+1-555-123-4567"
}

response = client.transaction_builder.add_buyer(transaction_id, buyer_data)
```

**Parameters:**
- `transaction_id` (str): Transaction builder ID
- `buyer_info` (Dict[str, Any]): Buyer information

#### `add_seller(transaction_id, seller_info)`

Add a seller to the transaction.

```python
seller_data = {
    "type": "SELLER",
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@email.com"
}

response = client.transaction_builder.add_seller(transaction_id, seller_data)
```

#### `add_co_agent(transaction_id, co_agent_info)`

Add a co-agent to the transaction.

```python
co_agent_data = {
    "agent_id": "agent-uuid-here",
    "role": "BUYERS_AGENT"
}

response = client.transaction_builder.add_co_agent(transaction_id, co_agent_data)
```

#### `add_participant(transaction_id, participant_info)`

Add other participants (inspectors, appraisers, etc.).

```python
participant_data = {
    "type": "INSPECTOR",
    "first_name": "Mike",
    "last_name": "Inspector",
    "company": "Quality Inspections Inc"
}

response = client.transaction_builder.add_participant(transaction_id, participant_data)
```

### Property & Transaction Details

#### `update_location_info(transaction_id, location_info)`

Update property location details.

```python
location_data = {
    "address": "123 Main Street",
    "city": "Anytown",
    "state": "CA",
    "zipCode": "90210",
    "county": "Los Angeles"
}

response = client.transaction_builder.update_location_info(transaction_id, location_data)
```

#### `update_price_and_date_info(transaction_id, price_date_info)`

Update pricing and date information.

```python
price_date_data = {
    "purchase_price": 750000,
    "closing_date": "2024-03-15",
    "contract_date": "2024-02-01"
}

response = client.transaction_builder.update_price_and_date_info(transaction_id, price_date_data)
```

#### `update_title_info(transaction_id, title_info)`

Update title company information.

```python
title_data = {
    "title_company": "Premier Title Co",
    "title_contact": "Sarah Johnson",
    "title_phone": "+1-555-789-0123"
}

response = client.transaction_builder.update_title_info(transaction_id, title_data)
```

### Commission & Financial Management

#### `update_commission_splits(transaction_id, commission_splits)`

Update commission split information.

```python
commission_data = [
    {
        "agent_id": "agent-uuid",
        "split_percentage": 50.0,
        "commission_amount": 15000
    }
]

response = client.transaction_builder.update_commission_splits(transaction_id, commission_data)
```

#### `add_commission_payer(transaction_id, commission_info)`

Add commission payer information.

```python
payer_data = {
    "payer_type": "SELLER",
    "commission_rate": 6.0
}

response = client.transaction_builder.add_commission_payer(transaction_id, payer_data)
```

### Query & List Operations

#### `get_transaction_builders(limit, from_offset, yenta_id, builder_type="TRANSACTION")`

Get paginated list of transaction builders.

```python
builders = client.transaction_builder.get_transaction_builders(
    limit=20,
    from_offset=0,
    yenta_id="user-id",
    builder_type="TRANSACTION"
)
```

---

## Transactions API

Work with live transactions, manage participants, and handle financial operations.

### Core Transaction Operations

#### `get_transaction(transaction_id)`

Get complete transaction details.

```python
transaction = client.transactions.get_transaction("tx-12345")
print(f"Status: {transaction['status']}")
print(f"Property: {transaction['property']['address']}")
```

#### `create_participant(transaction_id, participant_data)`

Add a new participant to an existing transaction.

```python
participant = {
    "type": "LENDER",
    "first_name": "Bank",
    "last_name": "Officer",
    "company": "First National Bank"
}

response = client.transactions.create_participant(transaction_id, participant)
```

### Financial Operations

#### `process_payment(transaction_id, payment_data)`

Process payments for a transaction.

```python
payment = {
    "amount": 5000.00,
    "type": "EARNEST_MONEY",
    "payment_method": "WIRE_TRANSFER"
}

response = client.transactions.process_payment(transaction_id, payment)
```

### Document & Reporting

#### `get_summary_pdf(transaction_id)`

Generate and retrieve transaction summary PDF.

```python
pdf_response = client.transactions.get_summary_pdf(transaction_id)
# pdf_response contains the PDF data
```

#### `get_transaction_documents(transaction_id)`

Get all documents associated with a transaction.

```python
documents = client.transactions.get_transaction_documents(transaction_id)
for doc in documents:
    print(f"Document: {doc['name']} - Type: {doc['type']}")
```

---

## Teams API

Search and manage team information.

### Team Search

#### `search_teams(**filters)`

Search for teams with comprehensive filtering.

```python
from rezen import TeamStatus, TeamType, SortDirection, SortField

# Basic search
teams = client.teams.search_teams(status="ACTIVE", limit=10)

# Advanced search with enums
teams = client.teams.search_teams(
    status=TeamStatus.ACTIVE,
    team_type=TeamType.PLATINUM,
    sort_by=[SortField.NAME, SortField.CREATED_AT],
    sort_direction=SortDirection.DESC,
    page_size=50
)

# Search by name and date range
teams = client.teams.search_teams(
    name="Sales Team",
    created_at_start="2024-01-01",
    created_at_end="2024-12-31"
)

# Text search
teams = client.teams.search_teams(
    search_text="marketing",
    page_number=2
)
```

**Parameters:**
- `page_number` (Optional[int]): Page number (default: 0)
- `page_size` (Optional[int]): Results per page (default: 20)
- `sort_direction` (Optional[SortDirection]): ASC or DESC
- `sort_by` (Optional[List[SortField]]): Fields to sort by
- `team_id` (Optional[str]): Filter by team UUID
- `name` (Optional[str]): Filter by team name
- `search_text` (Optional[str]): General search text
- `status` (Optional[TeamStatus]): ACTIVE or INACTIVE
- `created_at_start` (Optional[str]): Date filter start (YYYY-MM-DD)
- `created_at_end` (Optional[str]): Date filter end (YYYY-MM-DD)
- `team_type` (Optional[TeamType]): Team type filter

**Returns:** `Dict[str, Any]` - Paginated team search results

#### `get_team_without_agents(team_id)`

Get team details without agent information.

```python
team = client.teams.get_team_without_agents("team-uuid")
print(f"Team: {team['name']} - Status: {team['status']}")
```

---

## Agents API

Comprehensive agent search, network management, and detailed information retrieval.

### Agent Search

#### `search_active_agents(**filters)`

Search for active agents with filtering and sorting.

```python
from rezen import AgentSortDirection, AgentSortField, Country, StateOrProvince

# Basic search
agents = client.agents.search_active_agents(name="John", limit=10)

# Advanced search
agents = client.agents.search_active_agents(
    page_size=50,
    sort_by=[AgentSortField.LAST_NAME, AgentSortField.FIRST_NAME],
    sort_direction=AgentSortDirection.ASC,
    country=[Country.UNITED_STATES],
    state_or_province=[StateOrProvince.CALIFORNIA, StateOrProvince.TEXAS]
)
```

**Parameters:**
- `page_number` (Optional[int]): Page number (default: 0)
- `page_size` (Optional[int]): Results per page (default: 20)
- `sort_direction` (Optional[AgentSortDirection]): ASC or DESC
- `sort_by` (Optional[List[AgentSortField]]): Fields to sort by
- `name` (Optional[str]): Filter by agent name
- `country` (Optional[List[Country]]): Filter by country
- `state_or_province` (Optional[List[StateOrProvince]]): Filter by state/province

### Agent Information

#### `get_agents_by_email(email_address)`

Find agent(s) by email address.

```python
agents = client.agents.get_agents_by_email("agent@email.com")
```

#### `get_agents_by_ids(agent_ids)`

Get multiple agents by their IDs.

```python
agents = client.agents.get_agents_by_ids(["agent-1", "agent-2", "agent-3"])
```

### Network & Hierarchy

#### `get_sponsor_tree(agent_id)`

Get agent's sponsor tree (upline hierarchy).

```python
sponsor_tree = client.agents.get_sponsor_tree("agent-uuid")
```

#### `get_down_line_agents(agent_id, tier, **filters)`

Get agents in the downline by tier.

```python
from datetime import date

# Get tier 1 downline
downline = client.agents.get_down_line_agents(
    agent_id="agent-uuid",
    tier=1,
    status_in=["ACTIVE"],
    page_size=100
)

# Get with date filters
downline = client.agents.get_down_line_agents(
    agent_id="agent-uuid",
    tier=2,
    updated_at_from=date(2024, 1, 1),
    updated_at_to=date(2024, 12, 31)
)
```

#### `get_front_line_agents_info(agent_id)`

Get front line agents basic information.

```python
front_line = client.agents.get_front_line_agents_info("agent-uuid")
```

#### `get_network_size_by_tier(agent_id)`

Get network size statistics by tier.

```python
network_stats = client.agents.get_network_size_by_tier("agent-uuid")
```

### Financial & Tax Information

#### `get_payment_details(agent_id)`

Get agent's payment details.

```python
payment_info = client.agents.get_payment_details("agent-uuid")
```

#### `get_tax_forms_summary(agent_id)`

Get tax forms summary.

```python
tax_summary = client.agents.get_tax_forms_summary("agent-uuid")
```

#### `get_commission_plan(plan_id)`

Get commission plan details.

```python
plan = client.agents.get_commission_plan("plan-uuid")
```

---

## Exceptions

The ReZEN client provides specific exceptions for different error scenarios.

```python
from rezen.exceptions import (
    RezenError,           # Base exception
    AuthenticationError,  # Invalid API key
    ValidationError,      # Invalid request data
    NotFoundError,        # Resource not found
    RateLimitError,       # Rate limit exceeded
    ServerError,          # Server-side error
    NetworkError          # Network/connection issues
)

# Example error handling
try:
    transaction = client.transactions.get_transaction("invalid-id")
except AuthenticationError:
    print("Check your API key")
except NotFoundError:
    print("Transaction not found")
except ValidationError as e:
    print(f"Invalid request: {e}")
except RateLimitError:
    print("Rate limit exceeded - retry later")
except RezenError as e:
    print(f"API error: {e}")
```

---

## Data Types & Enums

### Team Enums

```python
from rezen import TeamStatus, TeamType, SortDirection, SortField

# Team status options
TeamStatus.ACTIVE
TeamStatus.INACTIVE

# Team types
TeamType.NORMAL
TeamType.PLATINUM
TeamType.GROUP
TeamType.DOMESTIC
TeamType.PRO

# Sort options
SortDirection.ASC
SortDirection.DESC

SortField.ID
SortField.NAME
SortField.STATUS
SortField.TEAM_TYPE
SortField.LEADER_NAME
SortField.CREATED_AT
```

### Agent Enums

```python
from rezen import AgentStatus, AgentSortDirection, AgentSortField, Country, StateOrProvince

# Agent status
AgentStatus.ACTIVE
AgentStatus.INACTIVE
AgentStatus.CANDIDATE
AgentStatus.REJECTED
AgentStatus.RESURRECTING

# Sort options
AgentSortDirection.ASC
AgentSortDirection.DESC

AgentSortField.ID
AgentSortField.FIRST_NAME
AgentSortField.LAST_NAME
AgentSortField.EMAIL_ADDRESS
AgentSortField.ACCOUNT_COUNTRY

# Geographic filters
Country.UNITED_STATES
Country.CANADA

StateOrProvince.CALIFORNIA
StateOrProvince.TEXAS
StateOrProvince.ONTARIO
# ... (all US states and Canadian provinces available)
```

---

## Example Workflows

### Complete Transaction Creation

```python
from rezen import RezenClient

client = RezenClient()

# 1. Create transaction builder
response = client.transaction_builder.create_transaction_builder()
transaction_id = response['id']

# 2. Add property details
location_data = {
    "address": "123 Main St",
    "city": "Anytown", 
    "state": "CA",
    "zipCode": "90210"
}
client.transaction_builder.update_location_info(transaction_id, location_data)

# 3. Add price and dates
price_data = {
    "purchase_price": 500000,
    "closing_date": "2024-06-15"
}
client.transaction_builder.update_price_and_date_info(transaction_id, price_data)

# 4. Add buyer
buyer_data = {
    "first_name": "John",
    "last_name": "Buyer",
    "email": "john@email.com"
}
client.transaction_builder.add_buyer(transaction_id, buyer_data)

# 5. Submit transaction
client.transaction_builder.submit_transaction(transaction_id)
```

### Agent Network Analysis

```python
# Find an agent
agents = client.agents.search_active_agents(name="Sarah", limit=1)
agent_id = agents[0]['id']

# Get their network
sponsor_tree = client.agents.get_sponsor_tree(agent_id)
front_line = client.agents.get_front_line_agents_info(agent_id)
network_stats = client.agents.get_network_size_by_tier(agent_id)

# Get downline agents
tier_1 = client.agents.get_down_line_agents(agent_id, tier=1)
tier_2 = client.agents.get_down_line_agents(agent_id, tier=2)

print(f"Network size: Tier 1: {len(tier_1)}, Tier 2: {len(tier_2)}")
```

---

**📝 Note:** This reference covers the most commonly used methods. For a complete list of all available methods and their parameters, use Python's built-in help:

```python
help(client.transaction_builder)
help(client.transactions)
help(client.teams)
help(client.agents)
``` 