# API Reference

Complete method reference for the ReZEN Python API client. This section covers all available API endpoints, parameters, and return types.

---

## 🚀 API Overview

<div class="grid cards" markdown>

-   :material-hammer-wrench:{ .lg .middle } **Transaction Builder**

    ---

    Create and manage transaction builders with participants and properties

    [:octicons-arrow-right-24: Transaction Builder API](transaction-builder.md)

-   :material-handshake:{ .lg .middle } **Transactions**

    ---

    Work with live transactions, manage participants, and handle payments

    [:octicons-arrow-right-24: Transactions API](transactions.md)

-   :material-account-group:{ .lg .middle } **Teams**

    ---

    Search and manage team information with comprehensive filtering

    [:octicons-arrow-right-24: Teams API](teams.md)

-   :material-account-tie:{ .lg .middle } **Agents**

    ---

    Agent search, network management, and detailed information retrieval

    [:octicons-arrow-right-24: Agents API](agents.md)

-   :material-book-open:{ .lg .middle } **Directory**

    ---

    Access directory services for agent and contact information

    [:octicons-arrow-right-24: Directory API](directory.md)

</div>

---

## 📋 Quick Reference

### Core Components

!!! abstract "Main Client"

    The **`RezenClient`** serves as the main entry point, providing access to all API modules through a unified interface.

!!! abstract "Specialized Clients"

    - **Transaction Builder**: Create and configure new transactions
    - **Transactions**: Manage live transactions and participants
    - **Teams**: Search and filter team information
    - **Agents**: Comprehensive agent search and network management
    - **Directory**: Standalone directory services

### Common Patterns

=== "Basic Usage"

    ```python
    from rezen import RezenClient

    # Initialize client
    client = RezenClient()

    # Access specialized APIs
    teams = client.teams.search_teams(status="ACTIVE")
    agents = client.agents.search_active_agents(name="John")
    ```

=== "Error Handling"

    ```python
    from rezen import RezenClient
    from rezen.exceptions import RezenError, NotFoundError

    try:
        client = RezenClient()
        transaction = client.transactions.get_transaction("tx-123")
    except NotFoundError:
        print("Transaction not found")
    except RezenError as e:
        print(f"API error: {e}")
    ```

=== "Advanced Filtering"

    ```python
    from rezen import RezenClient
    from rezen.enums import TeamStatus, SortDirection

    client = RezenClient()

    # Advanced team search with enums
    teams = client.teams.search_teams(
        status=TeamStatus.ACTIVE,
        sort_direction=SortDirection.DESC,
        page_size=50
    )
    ```

---

## 🔧 Client Setup

!!! info "Getting Started"

    Before using any API methods, you need to set up authentication. See the [Authentication Guide](../getting-started/authentication.md) for setup instructions.

### Quick Setup

```python
from rezen import RezenClient

# Using environment variable (recommended)
client = RezenClient()

# Or with explicit API key
client = RezenClient(api_key="your_api_key_here")
```

---

## 📖 API Endpoints by Category

### **🏗️ Transaction Management**
Build and manage real estate transactions:

- **[Transaction Builder](transaction-builder.md)** - Create new transactions with participants
- **[Transactions](transactions.md)** - Manage live transactions and processing

### **👥 People & Organizations**
Work with agents, teams, and contacts:

- **[Teams](teams.md)** - Search and manage team information
- **[Agents](agents.md)** - Agent search and network management
- **[Directory](directory.md)** - Contact and agent directory services

---

## 🎯 Key Features

### **Type Safety**
- Full type hints for all methods and parameters
- IDE autocompletion and error detection
- Runtime type validation with Pydantic

### **Error Handling**
- Specific exception types for different error conditions
- Rich error context with request/response details
- Comprehensive error handling patterns

### **Developer Experience**
- Google-style docstrings with examples
- Automatic retry logic for transient failures
- Built-in rate limiting and pagination support

---

## 📚 Related Documentation

!!! tip "Additional Resources"

    - **[Data Types & Enums](../reference/data-types.md)** - Type definitions and constants
    - **[Exception Reference](../reference/exceptions.md)** - Error handling guide
    - **[Examples & Guides](../guides/examples.md)** - Practical usage examples
    - **[Authentication Setup](../getting-started/authentication.md)** - Client configuration

---

## 🚀 Quick Start

New to the ReZEN API? Start here:

1. **[Install the client](../getting-started/installation.md)** - Get up and running
2. **[Configure authentication](../getting-started/authentication.md)** - Set up your API key
3. **[Try the quick start](../getting-started/quickstart.md)** - Make your first API call
4. **[Explore examples](../guides/examples.md)** - See real-world use cases

---

## 🔍 Method Lookup

Looking for a specific method? Use the search function above or browse by category:

- **Transaction creation** → [Transaction Builder](transaction-builder.md)
- **Agent search** → [Agents API](agents.md)
- **Team management** → [Teams API](teams.md)
- **Payment processing** → [Transactions API](transactions.md)
- **Contact lookup** → [Directory API](directory.md)
